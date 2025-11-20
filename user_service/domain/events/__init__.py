"""Domain events for User Service"""
from user_service.domain.events.events import (
    DomainEvent,
    UserCreated,
    UserUpdated,
    UserBlocked,
    UserAccessRestored,
    UserRoleChanged,
    DoctorAssignedToPatient,
)
from user_service.domain.events.event_bus import event_bus

__all__ = [
    "DomainEvent",
    "UserCreated",
    "UserUpdated",
    "UserBlocked",
    "UserAccessRestored",
    "UserRoleChanged",
    "DoctorAssignedToPatient",
    "event_bus",
]
