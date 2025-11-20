"""Use case: Block user"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User
from user_service.domain.events.events import UserBlocked
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository
from user_service.infrastructure.http_clients.auth_client import AuthServiceClient
from user_service.api.schemas import BlockUserRequest
import uuid


class BlockUserUseCase:
    """Use case for blocking a user"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.auth_client = AuthServiceClient()
        self.db = db
    
    async def execute(self, user_id: int, block_data: BlockUserRequest, blocked_by: int) -> User:
        """Execute block user use case"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already blocked"
            )
        
        # Block user
        user.is_blocked = True
        user.blocked_at = datetime.utcnow()
        user.blocked_by = blocked_by
        user = self.user_repo.update(user)
        
        # Emit domain event
        event = UserBlocked(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=user.id,
            blocked_by=blocked_by,
            reason=block_data.reason
        )
        event_bus.publish(event)
        
        # Synchronize with Auth Service
        await self.auth_client.block_user(user.auth_user_id, block_data.reason)
        
        return user

