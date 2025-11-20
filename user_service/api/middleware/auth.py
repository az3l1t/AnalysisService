"""Authentication and authorization middleware"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from user_service.infrastructure.database.database import get_db, settings
from user_service.infrastructure.repositories.user_repository import UserRepository
from user_service.infrastructure.http_clients.auth_client import AuthServiceClient
from user_service.api.schemas import TokenData
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode JWT token
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token payload missing 'sub' field")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен невалиден или истек. Получите новый токен в Auth Service.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        raise credentials_exception
    
    # Get user from User Service by auth_user_id
    # The JWT token from Auth Service contains "sub" (username) and "user_id"
    user_repo = UserRepository(db)
    
    # Try to get auth_user_id from token (Auth Service includes user_id)
    auth_user_id = payload.get("user_id") or payload.get("auth_user_id")
    
    logger.info(f"Token decoded - username: {username}, user_id: {auth_user_id}, payload keys: {list(payload.keys())}")
    
    # If user_id is not in token, try to find user by email (fallback)
    if not auth_user_id:
        logger.warning(f"user_id not found in token payload. Available keys: {list(payload.keys())}")
        logger.warning(f"Trying to find user by email: {username}")
        # Fallback: try to find user by email (assuming username might be email)
        user = user_repo.get_by_email(username)
        if user:
            logger.info(f"User found by email: {user.id}")
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден в User Service. Создайте пользователя с auth_user_id из Auth Service.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from User Service by auth_user_id
    try:
        user = user_repo.get_by_auth_user_id(auth_user_id)
        if user is None:
            logger.warning(f"User not found in User Service with auth_user_id: {auth_user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Пользователь с auth_user_id={auth_user_id} не найден в User Service. Создайте пользователя в User Service.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"User found: {user.id}, email: {user.email}, roles: {[r.name for r in user.roles]}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user from repository: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении пользователя: {str(e)}"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Get current active (non-blocked) user"""
    if current_user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )
    return current_user


async def get_auth_user_id_from_token(
    token: str = Depends(oauth2_scheme)
) -> int:
    """Get auth_user_id from JWT token without checking User Service"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode JWT token
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        auth_user_id = payload.get("user_id")
        if auth_user_id is None:
            logger.error("Token payload missing 'user_id' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит user_id. Получите новый токен в Auth Service.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return int(auth_user_id)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен невалиден или истек. Получите новый токен в Auth Service.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        raise credentials_exception


def require_role(role_name: str):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user = Depends(get_current_active_user)):
        if not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {role_name} role"
            )
        return current_user
    return role_checker


async def require_admin(current_user = Depends(get_current_active_user)):
    """Require admin role"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires ADMIN role"
        )
    return current_user


async def require_doctor_or_admin(current_user = Depends(get_current_active_user)):
    """Require doctor or admin role"""
    if not (current_user.is_doctor() or current_user.is_admin()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires DOCTOR or ADMIN role"
        )
    return current_user

