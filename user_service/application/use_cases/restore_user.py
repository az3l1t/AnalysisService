"""Use case: Restore user access"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User
from user_service.domain.events.events import UserAccessRestored
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository
from user_service.infrastructure.http_clients.auth_client import AuthServiceClient
import uuid


class RestoreUserUseCase:
    """Use case for restoring user access"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.auth_client = AuthServiceClient()
        self.db = db
    
    async def execute(self, user_id: int, restored_by: int) -> User:
        """Execute restore user use case"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not blocked"
            )
        
        # Restore user
        user.is_blocked = False
        user.blocked_at = None
        user.blocked_by = None
        user = self.user_repo.update(user)
        
        # Emit domain event
        event = UserAccessRestored(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=user.id,
            restored_by=restored_by
        )
        event_bus.publish(event)
        
        # Synchronize with Auth Service
        await self.auth_client.restore_user(user.auth_user_id)
        
        return user

