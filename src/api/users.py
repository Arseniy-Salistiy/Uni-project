from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extensions import connection

from src.schemas import CreateStudent, User, CreateTeacher
from src.services.user_service import get_user_service, UserService

router = APIRouter(prefix='/users')

@router.post('/signup/student', response_model=User)
def signup_students(credentials: CreateStudent, service: UserService = Depends(get_user_service)):
    return service.signup_student(credentials)

@router.post('/signup/teacher', response_model=User)
def signup_teachers(credentials: CreateTeacher, service: UserService = Depends(get_user_service)):
    return service.signup_teacher(credentials)
