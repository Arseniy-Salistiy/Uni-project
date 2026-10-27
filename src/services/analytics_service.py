from fastapi import Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from typing import List, Dict, Any

from src.repository.group_repository import GroupRepository
from src.repository.subject_repository import SubjectRepository
from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.student_repository import StudentRepository
from src.repository.analytics_repository import AnalyticsRepository
from src.schemas.analytics_schemas import *
from src.core.config import settings
from src.db.database import get_db

class AnalyticsService:
    def __init__(self, conn):
        self.group_repo = GroupRepository(conn)
        self.subject_repo = SubjectRepository(conn)
        self.course_assignment_repo = CourseAssignmentRepository(conn)
        self.student_repo = StudentRepository(conn)
        self.analytics_repo = AnalyticsRepository(conn)

    def get_group_subject_report(self, group_id: int, subject_id: int, is_final: bool) -> List[Dict[str, Any]]:
        self._check_group(group_id)
        self._check_subject(subject_id)
        return self.analytics_repo.get_group_subject_report(group_id, subject_id, is_final)

    def get_student_summary_report(self, student_id: int, cur_user: dict) -> List[Dict[str, Any]]:
        if cur_user.get('role_id') == settings.STUDENT and student_id != cur_user.get('id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Доступ запрещен')
        self._check_student(student_id)
        return self.analytics_repo.get_student_summary_report(student_id)

    def _check_student(self, student_id: int) -> None:
        if not self.student_repo.get_student_by_id(student_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Студент не найден')

    def _check_group(self, group_id: int) -> None:
        if not self.group_repo.get_group_by_id(group_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Группа не найдена')

    def _check_subject(self, subject_id: int) -> None:
        if not self.subject_repo.get_subject_by_id(subject_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Дисциплина не найдена')

def get_analytics_service(conn=Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(conn)