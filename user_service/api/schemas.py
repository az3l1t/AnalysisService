"""Pydantic schemas for User Service API"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    """Base user schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """Schema for creating a user"""
    auth_user_id: int = Field(..., description="ID from Auth Service")
    roles: List[str] = Field(default=["PATIENT"], description="List of role names")


class UserSelfRegister(UserBase):
    """Schema for self-registration (auth_user_id taken from token)"""
    roles: List[str] = Field(default=["PATIENT"], description="List of role names")


class UserUpdate(BaseModel):
    """Schema for updating user data"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class RoleResponse(BaseModel):
    """Role response schema"""
    id: int
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    """User response schema"""
    id: int
    auth_user_id: int
    is_blocked: bool
    roles: List[RoleResponse] = []
    assigned_doctor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    blocked_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Response schema for user list"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class RoleUpdate(BaseModel):
    """Schema for updating user roles"""
    roles: List[str] = Field(..., description="List of role names (PATIENT, DOCTOR, ADMIN)")


class AssignDoctorRequest(BaseModel):
    """Schema for assigning a doctor to a patient"""
    doctor_id: int = Field(..., description="ID of the doctor to assign")


class BlockUserRequest(BaseModel):
    """Schema for blocking a user"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for blocking")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
