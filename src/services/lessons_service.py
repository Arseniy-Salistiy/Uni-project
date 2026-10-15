from fastapi import Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from typing import Dict, Any, List

from src.repository.lesson_repository import LessonsRepository
from src.repository.group_repository import GroupRepository
from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.student_repository import StudentRepository
from src.schemas.lessons_schemas import *
from src.db.database import get_db

class LessonsService:
    def __init__(self, conn):
        self.lesson_repo = LessonsRepository(conn)
        self.group_repo = GroupRepository(conn)
        self.student_repo = StudentRepository(conn)
        self.course_assignment_repo = CourseAssignmentRepository(conn)

    def create_lesson(self, payload: CreateLesson) -> None | Dict[str, Any]:
        self._check_course_assignment(payload.course_assignment_id)
        return self.lesson_repo.create_lesson(payload)

    def get_lessons_by_group(self, group_id: int, lesson_date: LessonDate) -> None | List[Dict[str, Any]]:
        self._check_group_id(group_id)
        return self.lesson_repo.get_lessons_by_group(group_id, lesson_date)

    def update_lesson(self, lesson_id: int, payload: LessonPatch) -> None | Dict[str, Any]:
        self._check_lesson_id(lesson_id)
        self._check_course_assignment(payload.course_assignment_id)
        return self.lesson_repo.patch_lesson(lesson_id, payload)

    def delete_lesson(self, lesson_id: int) -> None | dict:
        self._check_lesson_id(lesson_id)
        return self.lesson_repo.delete_lesson(lesson_id)

    def mark_attendance(self, payload: CreateAttendance) -> None | Dict[str, Any]:
        self._check_student_id(payload.student_id)
        self._check_lesson_id(payload.lesson_id)
        try:
            return self.lesson_repo.mark_attendance(payload)
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Посещаемость уже выставлена')

    def get_attendance_by_student(self, course_id: int, student_id: int, timeline: StudentDate, filter: AttendanceFilter) -> None | List[Dict[str, Any]]:
        self._check_student_id(student_id)
        self._check_course_assignment(course_id)
        res = self.lesson_repo.get_attendence_by_student(course_id, student_id, timeline, filter)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Отметок посещаемости не найдено')
        return res

    def get_student_attendance_period(self, payload: AttendancePeriod) -> None | List[Dict[str, Any]]:
        self._check_student_id(payload.student_id)
        return self.lesson_repo.get_student_attendance_period(payload)

    def patch_attendance(self, attendance_id: int, payload: AttendancePatch) -> Dict[str, Any]:
        self._check_lesson_id(payload.lesson_id)
        self._check_student_id(payload.student_id)

        if not self.lesson_repo.get_attendance_by_id(attendance_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такой записи посещаемости нет')

        return self.lesson_repo.patch_attendance(attendance_id, payload)

    def _check_student_id(self, id: None | int) -> None:
        if id and not self.student_repo.get_student_by_id(id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого студента не существует')

    def _check_group_id(self, id: None | int) -> None:
        if id and self.group_repo.get_group_by_id(id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Группа не найдена')

    def _check_lesson_id(self, id: None | int) -> None:
        if id and not self.lesson_repo.get_lesson_by_id(id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такой пары нет')

    def _check_course_assignment(self, id: None | int) -> None:
        if id and self.course_assignment_repo.get_course_assignment_by_id(id) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Данная дисциплина не назначена данной группе')

def get_lessons_service(conn=Depends(get_db)) -> LessonsService:
    return LessonsService(conn)