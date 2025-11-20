"""User repository implementation"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from user_service.domain.models.user import User, Role


class UserRepository:
    """Repository for User aggregate"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """Create a new user"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        from sqlalchemy.orm import joinedload
        return self.db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
    
    def get_by_auth_user_id(self, auth_user_id: int) -> Optional[User]:
        """Get user by Auth Service user ID"""
        from sqlalchemy.orm import joinedload
        return self.db.query(User).options(joinedload(User.roles)).filter(User.auth_user_id == auth_user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update(self, user: User) -> User:
        """Update user"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Delete user"""
        self.db.delete(user)
        self.db.commit()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_blocked: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """List users with filters and pagination"""
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(User)
        
        # Eager load roles to avoid lazy loading issues
        query = query.options(joinedload(User.roles))
        
        # Apply filters
        if role:
            query = query.join(User.roles).filter(Role.name == role)
        
        if is_blocked is not None:
            query = query.filter(User.is_blocked == is_blocked)
        
        if search:
            search_filter = or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def get_doctors(self) -> List[User]:
        """Get all users with DOCTOR role"""
        return self.db.query(User).join(User.roles).filter(Role.name == "DOCTOR").all()
    
    def get_patients_by_doctor(self, doctor_id: int) -> List[User]:
        """Get all patients assigned to a specific doctor"""
        return self.db.query(User).filter(
            and_(
                User.assigned_doctor_id == doctor_id,
                User.is_blocked == False
            )
        ).all()


class RoleRepository:
    """Repository for Role entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def get_or_create(self, name: str, description: Optional[str] = None) -> Role:
        """Get role by name or create if not exists"""
        role = self.get_by_name(name)
        if not role:
            role = Role(name=name, description=description)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        return role
    
    def get_all(self) -> List[Role]:
        """Get all roles"""
        return self.db.query(Role).all()

