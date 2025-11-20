"""Use case: Create user"""
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User, Role
from user_service.domain.events.events import UserCreated
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository, RoleRepository
from user_service.api.schemas import UserCreate
import uuid


class CreateUserUseCase:
    """Use case for creating a new user"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.db = db
    
    def execute(self, user_data: UserCreate, created_by: int = None) -> User:
        """Execute create user use case"""
        # Check if user with this auth_user_id already exists
        existing_user = self.user_repo.get_by_auth_user_id(user_data.auth_user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with auth_user_id {user_data.auth_user_id} already exists"
            )
        
        # Check if email is already taken
        existing_email = self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            auth_user_id=user_data.auth_user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            email=user_data.email,
            phone=user_data.phone,
            is_blocked=False
        )
        
        # Assign roles
        role_objects = []
        for role_name in user_data.roles:
            role = self.role_repo.get_or_create(role_name)
            role_objects.append(role)
        
        user.roles = role_objects
        
        # Save user
        user = self.user_repo.create(user)
        
        # Emit domain event
        event = UserCreated(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=user.id,
            auth_user_id=user.auth_user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            phone=user.phone,
            roles=[role.name for role in user.roles]
        )
        event_bus.publish(event)
        
        return user

