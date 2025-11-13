import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Тестовая база данных в памяти (SQLite для тестов)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# Переопределяем настройки БД для тестов ПЕРЕД импортом app.database
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

# Теперь импортируем после установки переменной окружения
from app.database import Base, get_db
from app import models

# Создаем engine для тестов (SQLite)
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Импортируем app после настройки тестовой БД
from app.main import app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    """Создание тестовой БД для каждого теста"""
    # Удаляем все таблицы перед созданием новых
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    """Тестовый клиент"""
    return TestClient(app)

@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

