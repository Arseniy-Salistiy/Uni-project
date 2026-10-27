from fastapi import Depends, HTTPException, status

from src.core.auth import get_user
from src.core.config import settings

class Roles:
    def __init__(self, permitted_roles: list[int]):
        self.permitted_roles = permitted_roles

    def __call__(self, cur_user: dict = Depends(get_user)):
        if cur_user.get('role_id') not in self.permitted_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Доступ запрещен')
        return True

ALL_ROLES = [settings.ADMIN, settings.DEAN, settings.TEACHER, settings.STUDENT]

def check_course_owner(teacher_id: int, cur_user: dict) -> None:
    if cur_user.get('role_id') == settings.TEACHER and teacher_id != cur_user.get('id'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Эта дисциплина закреплена за другим преподавателем')

def check_self_student(student_id: int, cur_user: dict) -> None:
    if cur_user.get('role_id') == settings.STUDENT and student_id != cur_user.get('id'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Нельзя смотреть данные другого студента')
