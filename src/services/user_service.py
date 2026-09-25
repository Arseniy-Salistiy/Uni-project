from fastapi import Depends, HTTPException, status

from src.repository.department_repository import DepartmentRepository
from src.repository.group_repository import GroupRepository
from src.repository.student_repository import StudentRepository
from src.repository.teacher_repository import TeacherRepository
from src.repository.user_repository import UserRepository
from src.schemas import CreateUser, CreateTeacher, CreateStudent
from src.db.database import get_db

class UserService:
    def __init__(self, conn):
        self.conn = conn
        self.department_repo = DepartmentRepository(conn)
        self.group_repo = GroupRepository(conn)
        self.student_repo = StudentRepository(conn)
        self.teacher_repo = TeacherRepository(conn)
        self.user_repo = UserRepository(conn)

    def signup_student(self, schema: CreateStudent):
        self.validate_email_phone(schema.email, schema.phone)

        new_user = self.user_repo.create_user(schema)
        self.student_repo.create_student(new_user['id'], schema)

        return new_user

    def signup_teacher(self, schema: CreateTeacher):
        self.validate_email_phone(schema.email, schema.phone)

        new_user = self.user_repo.create_user(schema)
        self.teacher_repo.create_teacher(new_user['id'], schema)

        return new_user

    def fetch_user(self, email: str):
        user = self.user_repo.get_by_email(email)
        return user

    def validate_email_phone(self, email: str, phone: str):
        if self.user_repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email уже занят')
        if self.user_repo.get_by_phone(phone):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Номер телефона уже занят')

def get_user_service(conn=Depends(get_db)) -> UserService:
    return UserService(conn)