"""User management routes"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from user_service.infrastructure.database.database import get_db
from user_service.infrastructure.repositories.user_repository import UserRepository
from user_service.application.use_cases.create_user import CreateUserUseCase
from user_service.application.use_cases.update_user import UpdateUserUseCase
from user_service.application.use_cases.update_roles import UpdateUserRolesUseCase
from user_service.application.use_cases.assign_doctor import AssignDoctorUseCase
from user_service.application.use_cases.block_user import BlockUserUseCase
from user_service.application.use_cases.restore_user import RestoreUserUseCase
from user_service.api.middleware.auth import (
    get_current_active_user,
    require_admin,
    require_doctor_or_admin,
    get_auth_user_id_from_token
)
from user_service.api.schemas import (
    UserCreate,
    UserSelfRegister,
    UserUpdate,
    UserResponse,
    UserListResponse,
    RoleUpdate,
    AssignDoctorRequest,
    BlockUserRequest
)
from user_service.domain.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_self(
    user_data: UserSelfRegister,
    db: Session = Depends(get_db),
    auth_user_id: int = Depends(get_auth_user_id_from_token)
):
    """Register your own profile (requires valid Auth Service token)"""
    user_repo = UserRepository(db)
    
    # Check if user already exists
    existing_user = user_repo.get_by_auth_user_id(auth_user_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль уже создан. Используйте обновление профиля."
        )
    
    # Create user with auth_user_id from token
    user_create = UserCreate(
        auth_user_id=auth_user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        email=user_data.email,
        phone=user_data.phone,
        roles=user_data.roles
    )
    
    use_case = CreateUserUseCase(db)
    user = use_case.execute(user_create, created_by=None)  # Self-registration
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (Admin only)
    
    ⚠️ Для самостоятельной регистрации используйте POST /users/register
    Этот endpoint доступен только для администраторов, уже существующих в User Service.
    """
    use_case = CreateUserUseCase(db)
    user = use_case.execute(user_data, created_by=current_user.id)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID (self or admin)"""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only view their own profile unless they are admin
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    is_blocked: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List users with filters (Admin only)"""
    user_repo = UserRepository(db)
    skip = (page - 1) * page_size
    
    users, total = user_repo.list_users(
        skip=skip,
        limit=page_size,
        role=role,
        is_blocked=is_blocked,
        search=search
    )
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user data (self or admin)"""
    # Users can only update their own profile unless they are admin
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    use_case = UpdateUserUseCase(db)
    user = use_case.execute(user_id, user_data, updated_by=current_user.id)
    return user


@router.post("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user roles (Admin only)"""
    use_case = UpdateUserRolesUseCase(db)
    user = await use_case.execute(user_id, role_data, changed_by=current_user.id)
    return user


@router.post("/{patient_id}/assign-doctor", response_model=UserResponse)
async def assign_doctor(
    patient_id: int,
    request: AssignDoctorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """Assign a doctor to a patient (Doctor or Admin)"""
    use_case = AssignDoctorUseCase(db)
    patient = use_case.execute(patient_id, request.doctor_id, assigned_by=current_user.id)
    return patient


@router.post("/{user_id}/block", response_model=UserResponse)
async def block_user(
    user_id: int,
    block_data: BlockUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Block a user (Admin only)"""
    use_case = BlockUserUseCase(db)
    user = await use_case.execute(user_id, block_data, blocked_by=current_user.id)
    return user


@router.post("/{user_id}/restore", response_model=UserResponse)
async def restore_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Restore user access (Admin only)"""
    use_case = RestoreUserUseCase(db)
    user = await use_case.execute(user_id, restored_by=current_user.id)
    return user

