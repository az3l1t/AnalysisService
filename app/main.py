from datetime import timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, auth
from app.database import engine, get_db, settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при запуске приложения"""
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not create database tables: {e}")
        print("⚠️  Make sure PostgreSQL is running and DATABASE_URL is correct")
    yield

app = FastAPI(
    title="Medical Analysis Auth Service",
    description="Микросервис аутентификации и авторизации для системы хранения медицинских анализов",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    return auth.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Получение JWT токена для аутентификации"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@app.get("/health")
def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверка подключения к БД
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/")
def root():
    """Корневой endpoint - возвращает веб-интерфейс"""
    return FileResponse("app/static/index.html")

@app.get("/api")
def api_info():
    """Информация об API"""
    return {"message": "Medical Analysis Auth Service", "version": "1.0.0"}

