"""Use case: Update user roles"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User
from user_service.domain.events.events import UserRoleChanged
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository, RoleRepository
from user_service.infrastructure.http_clients.auth_client import AuthServiceClient
from user_service.api.schemas import RoleUpdate
import uuid


class UpdateUserRolesUseCase:
    """Use case for updating user roles"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.auth_client = AuthServiceClient()
        self.db = db
    
    async def execute(self, user_id: int, role_data: RoleUpdate, changed_by: int) -> User:
        """Execute update user roles use case"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        old_roles = [role.name for role in user.roles]
        
        # Update roles
        new_role_objects = []
        for role_name in role_data.roles:
            role = self.role_repo.get_or_create(role_name)
            new_role_objects.append(role)
        
        user.roles = new_role_objects
        user = self.user_repo.update(user)
        
        new_roles = [role.name for role in user.roles]
        
        # Emit domain event
        event = UserRoleChanged(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=user.id,
            old_roles=old_roles,
            new_roles=new_roles,
            changed_by=changed_by
        )
        event_bus.publish(event)
        
        # Synchronize with Auth Service
        await self.auth_client.update_user_roles(user.auth_user_id, new_roles)
        
        return user

