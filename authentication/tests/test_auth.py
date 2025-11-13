import pytest
from fastapi import status
from app import auth, schemas

class TestPasswordHashing:
    """Юнит-тесты для хеширования паролей"""
    
    def test_hash_password(self):
        """Тест хеширования пароля"""
        password = "testpassword123"
        hashed = auth.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Тест проверки правильного пароля"""
        password = "testpassword123"
        hashed = auth.get_password_hash(password)
        assert auth.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Тест проверки неправильного пароля"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = auth.get_password_hash(password)
        assert auth.verify_password(wrong_password, hashed) is False

class TestTokenCreation:
    """Юнит-тесты для создания токенов"""
    
    def test_create_access_token(self):
        """Тест создания access token"""
        data = {"sub": "testuser"}
        token = auth.create_access_token(data=data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

