from fastapi import Depends, HTTPException, status
from typing import Dict, Any, List
from psycopg2.errors import UniqueViolation

from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.group_repository import GroupRepository
from src.repository.subject_repository import SubjectRepository
from src.repository.teacher_repository import TeacherRepository
from src.schemas.course_schemas import CreateCourseAssignment
from src.db.database import get_db

class CourseAssignmentService:
    def __init__(self, conn):
        self.course_assignment_repo = CourseAssignmentRepository(conn)
        self.group_repo = GroupRepository(conn)
        self.subject_repo = SubjectRepository(conn)
        self.teacher_repo = TeacherRepository(conn)

    def assign_course(self, data: CreateCourseAssignment) -> None | Dict[str, Any]:
        if not self.group_repo.get_group_by_id(data.group_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Группа не существует')
        if not self.subject_repo.get_subject_by_id(data.subject_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Предмет не существует')
        if not self.teacher_repo.get_teacher_by_id(data.teacher_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Преподаватель не существует')

        try:
            return self.course_assignment_repo.assign_course(data)
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Дисциплина уже назначена')

    def get_assignments_for_group(self, group_id: int) -> None | List[Dict[str, Any]]:
        if not self.group_repo.get_group_by_id(group_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Группа не найдена')

        res = self.course_assignment_repo.get_assignments_for_group(group_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='У данной группы нет назначенных дисциплин')
        return res

def get_course_assignment_service(conn=Depends(get_db)) -> CourseAssignmentService:
    return CourseAssignmentService(conn)