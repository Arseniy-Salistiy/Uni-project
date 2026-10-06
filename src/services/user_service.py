from fastapi import Depends, HTTPException, status
from typing import Dict, Any

from src.repository.department_repository import DepartmentRepository
from src.repository.group_repository import GroupRepository
from src.repository.student_repository import StudentRepository
from src.repository.teacher_repository import TeacherRepository
from src.repository.user_repository import UserRepository
from src.schemas.user_schemas import CreateUser, CreateTeacher, CreateStudent, TeacherPatch, StudentPatch, UserPatch
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

    def fetch_student_by_id(self, student_id: int) -> None | Dict[str, Any]:
        student = self.student_repo.get_student_by_id(student_id)

        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого студента нет')
        return student

    def fetch_teacher_by_id(self, teacher_id: int) -> None | Dict[str, Any]:
        teacher = self.teacher_repo.get_teacher_by_id(teacher_id)

        if teacher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Преподаватель не найден')
        return teacher

    def patch_teacher_info(self, teacher_id: int, payload: TeacherPatch):
        return self.teacher_repo.update_teacher_info(teacher_id, payload)

    def patch_student_info(self, student_id: int, payload: StudentPatch):
        return self.student_repo.update_student_info(student_id, payload)

    def patch_user_info(self, user_id: int, payload: UserPatch):
        return self.user_repo.change_profile_info(user_id, payload)

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