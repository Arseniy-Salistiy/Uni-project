from fastapi import APIRouter, Depends, HTTPException

from src.schemas.user_schemas import CreateStudent, User, StudentPatch
from src.services.user_service import UserService, get_user_service
from src.repository.student_repository import StudentRepository, get_student_repo

router = APIRouter(prefix='/students', tags=['students'])

@router.get('/')
def get_all_students(student_repo: StudentRepository = Depends(get_student_repo)):
    return student_repo.get_all_students()

@router.post('/signup', response_model=User)
def signup_student(credentials: CreateStudent, service: UserService = Depends(get_user_service)):
    return service.signup_student(credentials)

@router.get('/{id}')
def get_student_by_id(id: int, service: UserService = Depends(get_user_service)):
    return service.fetch_student_by_id(id)

@router.patch('/{id}/status')
def change_student_status(id: int, payload: StudentPatch, service: UserService = Depends(get_user_service)):
    return service.patch_student_info(id, payload)