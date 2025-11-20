"""Domain events for User Service"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class DomainEvent:
    """Base class for domain events"""
    event_id: str
    occurred_at: datetime
    aggregate_id: int  # User ID


@dataclass
class UserCreated(DomainEvent):
    """Event emitted when a user is created"""
    auth_user_id: int  # ID from Auth Service
    email: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    roles: List[str] = None  # List of role names


@dataclass
class UserUpdated(DomainEvent):
    """Event emitted when user data is updated"""
    updated_fields: dict  # Fields that were updated
    updated_by: int  # User ID who made the update


@dataclass
class UserRoleChanged(DomainEvent):
    """Event emitted when user roles are changed"""
    old_roles: List[str]
    new_roles: List[str]
    changed_by: int  # User ID who made the change


@dataclass
class DoctorAssignedToPatient(DomainEvent):
    """Event emitted when a doctor is assigned to a patient"""
    patient_id: int
    doctor_id: int
    assigned_by: int  # User ID who made the assignment


@dataclass
class UserBlocked(DomainEvent):
    """Event emitted when a user is blocked"""
    blocked_by: int  # User ID who blocked
    reason: Optional[str] = None


@dataclass
class UserAccessRestored(DomainEvent):
    """Event emitted when user access is restored"""
    restored_by: int  # User ID who restored access

