"""Database base configuration"""
# Import Base from models to ensure it's created
from user_service.domain.models.user import Base

__all__ = ["Base"]
