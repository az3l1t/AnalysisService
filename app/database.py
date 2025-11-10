from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/auth_db",
        alias="DATABASE_URL"
    )
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()

# Создаем engine с настройками для работы без подключения при старте
# Добавляем параметры для принудительного использования IPv4 и улучшенной работы с Supabase
connect_args = {
    "connect_timeout": 10,  # Увеличиваем таймаут до 10 секунд
    "sslmode": "require",   # Требуем SSL для Supabase
}

# Если используется connection pooler, добавляем соответствующие параметры
database_url = settings.database_url
if "?pgbouncer=true" in database_url or ":6543" in database_url:
    # Connection pooler mode - используем разные настройки
    connect_args["server_settings"] = {"jit": "off"}
else:
    # Прямое подключение - добавляем параметры для IPv4
    if "?" in database_url:
        database_url += "&"
    else:
        database_url += "?"
    database_url += "sslmode=require"

engine = create_engine(
    database_url,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,  # Размер пула соединений
    max_overflow=10,  # Максимальное количество дополнительных соединений
    pool_recycle=3600,  # Переиспользование соединений каждый час
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

