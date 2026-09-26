from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from psycopg2.extensions import connection

from src.schemas.user_schemas import CreateStudent, User, CreateTeacher
from src.services.user_service import get_user_service, UserService
from src.repository.teacher_repository import TeacherRepository, get_teacher_repo
from src.repository.student_repository import StudentRepository, get_student_repo
from src.core.auth import *

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=User)
def get_myself(current_user: User = Depends(get_user)):
    return current_user

@router.get('/teachers')
def get_teachers(teacher_repo: TeacherRepository = Depends(get_teacher_repo)):
    return teacher_repo.get_all_teachers()

@router.get('/students')
def get_students(student_repo: StudentRepository = Depends(get_student_repo)):
    return student_repo.get_all_students()

@router.post('/signup/student', response_model=User)
def signup_students(credentials: CreateStudent, service: UserService = Depends(get_user_service)):
    return service.signup_student(credentials)

@router.post('/signup/teacher', response_model=User)
def signup_teachers(credentials: CreateTeacher, service: UserService = Depends(get_user_service)):
    return service.signup_teacher(credentials)

@router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
    user = service.fetch_user(form_data.username)
    if not user or not verify_password(form_data.password, user.get('password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверный пароль или email',
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token({"sub": user.get('email'), "role": user.get('role_id'), "id": user.get('id')})
    return {"access_token": access_token}

@router.post('/logout')
def logout():
    pass