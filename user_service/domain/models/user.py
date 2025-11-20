"""User domain model"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Association table for many-to-many relationship: User <-> Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_profiles.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class User(Base):
    """User aggregate root"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(Integer, unique=True, index=True, nullable=False)  # Reference to Auth Service user
    
    # Personal information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True, index=True)
    
    # Status
    is_blocked = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    blocked_at = Column(DateTime(timezone=True), nullable=True)
    blocked_by = Column(Integer, ForeignKey('user_profiles.id'), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    assigned_doctor_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=True)
    assigned_doctor = relationship("User", remote_side=[id], foreign_keys=[assigned_doctor_id], backref="patients")
    # patients relationship is handled by backref from assigned_doctor
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.first_name} {self.last_name})>"
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def is_patient(self) -> bool:
        """Check if user is a patient"""
        return self.has_role("PATIENT")
    
    def is_doctor(self) -> bool:
        """Check if user is a doctor"""
        return self.has_role("DOCTOR")
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.has_role("ADMIN")


class Role(Base):
    """Role entity"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # PATIENT, DOCTOR, ADMIN
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"

