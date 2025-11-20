"""HTTP client for Auth Service integration"""
import httpx
from typing import Optional, Dict, Any
from user_service.infrastructure.database.database import settings
import logging

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Client for communicating with Auth Service"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.auth_service_url
        self.timeout = 10.0
    
    async def update_user_roles(self, auth_user_id: int, roles: list[str]) -> bool:
        """
        Update user roles in Auth Service
        This is a placeholder - Auth Service needs to implement this endpoint
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # This endpoint should be implemented in Auth Service
                response = await client.post(
                    f"{self.base_url}/users/{auth_user_id}/roles",
                    json={"roles": roles}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to update user roles in Auth Service: {e}")
            return False
    
    async def block_user(self, auth_user_id: int, reason: Optional[str] = None) -> bool:
        """
        Block user in Auth Service
        This invalidates tokens and prevents login
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # This endpoint should be implemented in Auth Service
                response = await client.post(
                    f"{self.base_url}/users/{auth_user_id}/block",
                    json={"reason": reason}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to block user in Auth Service: {e}")
            return False
    
    async def restore_user(self, auth_user_id: int) -> bool:
        """
        Restore user access in Auth Service
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # This endpoint should be implemented in Auth Service
                response = await client.post(
                    f"{self.base_url}/users/{auth_user_id}/restore"
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to restore user in Auth Service: {e}")
            return False
    
    async def get_user_by_id(self, auth_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user from Auth Service by ID
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{auth_user_id}")
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Failed to get user from Auth Service: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user from Auth Service by username
        This calls /users/me endpoint or a dedicated endpoint if available
        Note: This requires a valid token, so it's better to include user_id in JWT token
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Auth Service might have an endpoint to get user by username
                # For now, we'll try /users/me which requires token
                # In production, Auth Service should include user_id in JWT token
                response = await client.get(f"{self.base_url}/users/me")
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Failed to get user by username from Auth Service: {e}")
            return None

