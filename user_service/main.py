"""Main application entry point for User Service"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from user_service.infrastructure.database.database import engine, get_db
from user_service.infrastructure.database.base import Base
from user_service.api.routes.users import router as users_router
from user_service.application.services.auth_event_handler import setup_auth_event_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Setup event handlers for Auth Service events
        setup_auth_event_handlers()
        print("✅ Auth Service event handlers registered")
    except Exception as e:
        print(f"⚠️  Warning: Could not create database tables: {e}")
        print("⚠️  Make sure PostgreSQL is running and USER_SERVICE_DATABASE_URL is correct")
    yield


app = FastAPI(
    title="Medical Analysis User Service",
    description="Микросервис управления пользователями для системы хранения медицинских анализов",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="user_service/api/static"), name="static")

# Include routers
app.include_router(users_router)


@app.get("/")
def root():
    """Root endpoint - возвращает веб-интерфейс"""
    return FileResponse("user_service/api/static/index.html")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "user-service"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "service": "user-service",
            "error": str(e)
        }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Medical Analysis User Service",
        "version": "1.0.0",
        "docs": "/docs"
    }

