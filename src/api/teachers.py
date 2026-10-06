from fastapi import APIRouter, Depends, HTTPException

from src.schemas.user_schemas import User, CreateTeacher, TeacherPatch
from src.services.user_service import UserService, get_user_service
from src.repository.teacher_repository import TeacherRepository, get_teacher_repo
from src.core.roles import Roles
from src.core.config import settings

router = APIRouter(prefix='/teachers', tags=['teachers'])

@router.get('/')
def get_all_teachers(teacher_repo: TeacherRepository = Depends(get_teacher_repo)):
    return teacher_repo.get_all_teachers()

@router.post('/signup', response_model=User)
def signup_teacher(credentials: CreateTeacher, service: UserService = Depends(get_user_service)):
    return service.signup_teacher(credentials)

@router.get('/{id}')
def get_teacher_by_id(id: int, service: UserService = Depends(get_user_service)):
    return service.fetch_teacher_by_id(id)

@router.patch('/{id}/info')
def change_teacher_info(teacher_id: int, payload: TeacherPatch,
                        role_check: bool = Depends(Roles([settings.ADMIN, settings.DEAN])),
                        service: UserService = Depends(get_user_service)):
    return service.patch_teacher_info(teacher_id, payload)