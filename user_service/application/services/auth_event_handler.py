"""Event handlers for Auth Service events"""
from sqlalchemy.orm import Session
from user_service.infrastructure.database.database import SessionLocal
from user_service.infrastructure.repositories.user_repository import UserRepository, RoleRepository
from user_service.domain.events.event_bus import event_bus
from user_service.application.use_cases.create_user import CreateUserUseCase
from user_service.api.schemas import UserCreate
import logging

logger = logging.getLogger(__name__)


def handle_auth_user_registered(event_data: dict):
    """
    Handle AuthUserRegistered event from Auth Service
    This is a placeholder - in production, you'd subscribe to actual event bus/message queue
    """
    try:
        db = SessionLocal()
        try:
            # Check if user already exists
            user_repo = UserRepository(db)
            existing_user = user_repo.get_by_auth_user_id(event_data.get("user_id"))
            if existing_user:
                logger.info(f"User with auth_user_id {event_data.get('user_id')} already exists")
                return
            
            # Create user in User Service
            user_data = UserCreate(
                auth_user_id=event_data.get("user_id"),
                email=event_data.get("email"),
                first_name=event_data.get("first_name", ""),
                last_name=event_data.get("last_name", ""),
                roles=["PATIENT"]  # Default role
            )
            
            use_case = CreateUserUseCase(db)
            # Note: created_by is set to the user itself (self-registration)
            user = use_case.execute(user_data, created_by=event_data.get("user_id"))
            logger.info(f"Created user {user.id} from Auth Service event")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling AuthUserRegistered event: {e}")


def setup_auth_event_handlers():
    """
    Setup event handlers for Auth Service events
    In production, this would subscribe to a message queue (RabbitMQ, Kafka, etc.)
    For now, this is a placeholder that shows how events would be handled
    """
    # In a real implementation, you would:
    # 1. Subscribe to message queue/topic for Auth Service events
    # 2. Parse incoming events
    # 3. Call appropriate handlers
    
    # Example: If using a message queue
    # message_queue.subscribe("auth.user.registered", handle_auth_user_registered)
    # message_queue.subscribe("auth.user.verified", handle_auth_user_verified)
    
    logger.info("Auth Service event handlers setup (placeholder)")

