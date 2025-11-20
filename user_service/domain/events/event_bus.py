"""Event bus for domain events"""
from typing import List, Callable, Any
from user_service.domain.events.events import DomainEvent
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-memory event bus for domain events"""
    
    def __init__(self):
        self._handlers: dict[type, List[Callable]] = {}
    
    def subscribe(self, event_type: type, handler: Callable[[DomainEvent], None]):
        """Subscribe handler to event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent):
        """Publish domain event"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {event_type.__name__}: {e}")


# Global event bus instance
event_bus = EventBus()

