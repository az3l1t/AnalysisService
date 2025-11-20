from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

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
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=False,
        extra="ignore"  # Игнорировать лишние переменные из .env (USER_SERVICE_DATABASE_URL, AUTH_SERVICE_URL)
    )

settings = Settings()

# Создаем engine с настройками для работы без подключения при старте
# Очищаем URL от параметров, которые не поддерживает psycopg3
database_url = settings.database_url

# Парсим URL и удаляем неподдерживаемые параметры
try:
    parsed = urlparse(database_url)
    if parsed.query:
        # Парсим query параметры
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        # Удаляем параметры, которые psycopg3 не поддерживает
        unsupported_params = ['server_settings', 'pgbouncer', 'sslmode']
        # Находим и удаляем все ключи (с учетом регистра)
        keys_to_remove = []
        for key in query_params.keys():
            if any(key.lower() == param.lower() for param in unsupported_params):
                keys_to_remove.append(key)
        for key in keys_to_remove:
            query_params.pop(key, None)
        
        # Собираем URL обратно
        if query_params:
            # Преобразуем обратно в строку query
            new_query = urlencode(query_params, doseq=True)
            database_url = urlunparse(parsed._replace(query=new_query))
        else:
            # Если параметров не осталось, удаляем query часть
            database_url = urlunparse(parsed._replace(query=''))
except Exception:
    # Если парсинг не удался, просто удаляем проблемные параметры через regex
    import re
    # Удаляем server_settings и другие неподдерживаемые параметры
    database_url = re.sub(r'[?&](server_settings|pgbouncer|sslmode)=[^&]*', '', database_url)
    # Очищаем возможные двойные разделители
    database_url = re.sub(r'\?&+', '?', database_url)
    database_url = re.sub(r'&+', '&', database_url)
    # Удаляем ведущий или завершающий разделитель
    database_url = re.sub(r'\?$', '', database_url)
    database_url = re.sub(r'&$', '', database_url)

# Настройки подключения
# psycopg3 не поддерживает server_settings и другие параметры в connect_args
connect_args = {
    "connect_timeout": 10,  # Таймаут подключения 10 секунд
}

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

