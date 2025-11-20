"""Use case: Assign doctor to patient"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from user_service.domain.models.user import User
from user_service.domain.events.events import DoctorAssignedToPatient
from user_service.domain.events.event_bus import event_bus
from user_service.infrastructure.repositories.user_repository import UserRepository
import uuid


class AssignDoctorUseCase:
    """Use case for assigning a doctor to a patient"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db
    
    def execute(self, patient_id: int, doctor_id: int, assigned_by: int) -> User:
        """Execute assign doctor use case"""
        patient = self.user_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        if not patient.is_patient():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a patient"
            )
        
        doctor = self.user_repo.get_by_id(doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        if not doctor.is_doctor():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a doctor"
            )
        
        # Assign doctor
        patient.assigned_doctor_id = doctor_id
        patient = self.user_repo.update(patient)
        
        # Emit domain event
        event = DoctorAssignedToPatient(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=patient.id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            assigned_by=assigned_by
        )
        event_bus.publish(event)
        
        return patient

