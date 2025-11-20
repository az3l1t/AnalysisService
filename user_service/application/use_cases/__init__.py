"""Use cases for User Service"""
from user_service.application.use_cases.create_user import CreateUserUseCase
from user_service.application.use_cases.update_user import UpdateUserUseCase
from user_service.application.use_cases.update_roles import UpdateUserRolesUseCase
from user_service.application.use_cases.assign_doctor import AssignDoctorUseCase
from user_service.application.use_cases.block_user import BlockUserUseCase
from user_service.application.use_cases.restore_user import RestoreUserUseCase

__all__ = [
    "CreateUserUseCase",
    "UpdateUserUseCase",
    "UpdateUserRolesUseCase",
    "AssignDoctorUseCase",
    "BlockUserUseCase",
    "RestoreUserUseCase",
]
