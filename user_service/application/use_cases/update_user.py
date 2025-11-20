"""Use case: Update user"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User
from user_service.domain.events.events import UserUpdated
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository
from user_service.api.schemas import UserUpdate
import uuid


class UpdateUserUseCase:
    """Use case for updating user data"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db
    
    def execute(self, user_id: int, user_data: UserUpdate, updated_by: int) -> User:
        """Execute update user use case"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Track updated fields
        updated_fields = {}
        
        # Update fields
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
            updated_fields["first_name"] = user_data.first_name
        
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
            updated_fields["last_name"] = user_data.last_name
        
        if user_data.middle_name is not None:
            user.middle_name = user_data.middle_name
            updated_fields["middle_name"] = user_data.middle_name
        
        if user_data.phone is not None:
            user.phone = user_data.phone
            updated_fields["phone"] = user_data.phone
        
        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = self.user_repo.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email
            updated_fields["email"] = user_data.email
        
        if updated_fields:
            user = self.user_repo.update(user)
            
            # Emit domain event
            event = UserUpdated(
                event_id=str(uuid.uuid4()),
                occurred_at=datetime.utcnow(),
                aggregate_id=user.id,
                updated_fields=updated_fields,
                updated_by=updated_by
            )
            event_bus.publish(event)
        
        return user

