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
# Добавляем параметры для улучшенной работы с Supabase
database_url = settings.database_url

# Удаляем параметр pgbouncer=true из URL, если он есть
# psycopg3 не поддерживает этот параметр, connection pooler работает через порт 6543
import re
# Удаляем ?pgbouncer=true или &pgbouncer=true из URL
database_url = re.sub(r'[?&]pgbouncer=true', '', database_url)
# Удаляем ведущий ? если он остался после удаления параметра
database_url = re.sub(r'\?$', '', database_url)

# Настройки подключения для Supabase
# psycopg3 не поддерживает server_settings в connect_args
connect_args = {
    "connect_timeout": 10,  # Увеличиваем таймаут до 10 секунд
}

# Connection pooler (порт 6543) работает без дополнительных настроек
# JIT отключение не требуется для connection pooler

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

