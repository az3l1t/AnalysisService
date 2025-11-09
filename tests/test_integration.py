import pytest
from fastapi import status

class TestUserRegistration:
    """Интеграционные тесты для регистрации пользователей"""
    
    def test_register_user_success(self, client, test_user_data):
        """Тест успешной регистрации пользователя"""
        response = client.post("/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_username(self, client, test_user_data):
        """Тест регистрации с дублирующимся username"""
        # Первая регистрация
        client.post("/register", json=test_user_data)
        # Вторая регистрация с тем же username
        response = client.post("/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_email(self, client, test_user_data):
        """Тест регистрации с дублирующимся email"""
        # Первая регистрация
        client.post("/register", json=test_user_data)
        # Вторая регистрация с другим username, но тем же email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "anotheruser"
        response = client.post("/register", json=duplicate_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestUserAuthentication:
    """Интеграционные тесты для аутентификации пользователей"""
    
    def test_login_success(self, client, test_user_data):
        """Тест успешного входа"""
        # Регистрация пользователя
        client.post("/register", json=test_user_data)
        # Вход
        response = client.post(
            "/token",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user_data):
        """Тест входа с неправильным паролем"""
        # Регистрация пользователя
        client.post("/register", json=test_user_data)
        # Вход с неправильным паролем
        response = client.post(
            "/token",
            data={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        response = client.post(
            "/token",
            data={
                "username": "nonexistent",
                "password": "password"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestProtectedEndpoints:
    """Интеграционные тесты для защищенных endpoints"""
    
    def test_get_current_user_success(self, client, test_user_data):
        """Тест получения информации о текущем пользователе"""
        # Регистрация и получение токена
        client.post("/register", json=test_user_data)
        token_response = client.post(
            "/token",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        token = token_response.json()["access_token"]
        
        # Запрос защищенного endpoint
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user_data["username"]
    
    def test_get_current_user_no_token(self, client):
        """Тест доступа без токена"""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Тест доступа с невалидным токеном"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestHealthCheck:
    """Тесты для health check"""
    
    def test_health_check(self, client):
        """Тест health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        # Health check может показать "degraded" если основная БД недоступна,
        # но endpoint должен работать
        assert data["status"] in ["healthy", "degraded"]
        # Проверяем, что есть информация о статусе БД
        assert "database" in data
    
    def test_root_endpoint(self, client):
        """Тест корневого endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # Корневой endpoint теперь возвращает HTML интерфейс
        assert response.headers["content-type"].startswith("text/html")
        assert "Auth" in response.text

