"""Database configuration for User Service"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re


class Settings(BaseSettings):
    """Application settings"""
    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/user_db",
        alias="USER_SERVICE_DATABASE_URL"
    )
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    
    # Auth Service integration
    auth_service_url: str = Field(
        default="http://localhost:8000",
        alias="AUTH_SERVICE_URL"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=False,
        extra="ignore"  # Игнорировать лишние переменные из .env
    )


settings = Settings()

# Clean database URL from unsupported parameters (same as Auth Service)
database_url = settings.database_url

try:
    parsed = urlparse(database_url)
    if parsed.query:
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        unsupported_params = ['server_settings', 'pgbouncer', 'sslmode']
        keys_to_remove = []
        for key in query_params.keys():
            if any(key.lower() == param.lower() for param in unsupported_params):
                keys_to_remove.append(key)
        for key in keys_to_remove:
            query_params.pop(key, None)
        
        if query_params:
            new_query = urlencode(query_params, doseq=True)
            database_url = urlunparse(parsed._replace(query=new_query))
        else:
            database_url = urlunparse(parsed._replace(query=''))
except Exception:
    database_url = re.sub(r'[?&](server_settings|pgbouncer|sslmode)=[^&]*', '', database_url)
    database_url = re.sub(r'\?&+', '?', database_url)
    database_url = re.sub(r'&+', '&', database_url)
    database_url = re.sub(r'\?$', '', database_url)
    database_url = re.sub(r'&$', '', database_url)

# Connection settings
connect_args = {
    "connect_timeout": 10,
}

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

