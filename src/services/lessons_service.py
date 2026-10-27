from fastapi import Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from typing import Dict, Any, List

from src.repository.lesson_repository import LessonsRepository
from src.repository.group_repository import GroupRepository
from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.student_repository import StudentRepository
from src.schemas.lessons_schemas import *
from src.core.roles import check_course_owner, check_self_student
from src.db.database import get_db

class LessonsService:
    def __init__(self, conn):
        self.lesson_repo = LessonsRepository(conn)
        self.group_repo = GroupRepository(conn)
        self.student_repo = StudentRepository(conn)
        self.course_assignment_repo = CourseAssignmentRepository(conn)

    def create_lesson(self, payload: CreateLesson, cur_user: dict) -> None | Dict[str, Any]:
        self._check_course_assignment(payload.course_assignment_id)
        self._check_course_owner(payload.course_assignment_id, cur_user)
        return self.lesson_repo.create_lesson(payload, cur_user['id'])

    def get_lessons_by_group(self, group_id: int, lesson_date: LessonDate) -> None | List[Dict[str, Any]]:
        self._check_group_id(group_id)
        return self.lesson_repo.get_lessons_by_group(group_id, lesson_date)

    def update_lesson(self, lesson_id: int, cur_user: dict, payload: LessonPatch) -> None | Dict[str, Any]:
        self._check_not_empty(payload)
        self._check_lesson_id(lesson_id)
        self._check_lesson_owner(lesson_id, cur_user)
        self._check_course_assignment(payload.course_assignment_id)
        if payload.course_assignment_id:
            self._check_course_owner(payload.course_assignment_id, cur_user)
        return self.lesson_repo.patch_lesson(lesson_id, cur_user['id'], payload)

    def delete_lesson(self, lesson_id: int, cur_user: dict) -> None | dict:
        self._check_lesson_id(lesson_id)
        self._check_lesson_owner(lesson_id, cur_user)
        return self.lesson_repo.delete_lesson(lesson_id, cur_user['id'])

    def mark_attendance(self, payload: CreateAttendance, cur_user: dict) -> None | Dict[str, Any]:
        self._check_student_id(payload.student_id)
        self._check_lesson_id(payload.lesson_id)
        lesson = self._check_lesson_owner(payload.lesson_id, cur_user)
        student = self.student_repo.get_student_by_id(payload.student_id)
        if student.get('group_id') != lesson.get('group_id'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Студент не учится в группе, у которой это занятие')
        try:
            return self.lesson_repo.mark_attendance(payload)
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Посещаемость уже выставлена')

    def get_attendance_by_student(self, course_id: int, student_id: int, timeline: StudentDate, filter: AttendanceFilter, cur_user: dict) -> None | List[Dict[str, Any]]:
        check_self_student(student_id, cur_user)
        self._check_student_id(student_id)
        self._check_course_assignment(course_id)
        res = self.lesson_repo.get_attendence_by_student(course_id, student_id, timeline, filter)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Отметок посещаемости не найдено')
        return res

    def get_student_attendance_period(self, payload: AttendancePeriod, cur_user: dict) -> None | List[Dict[str, Any]]:
        check_self_student(payload.student_id, cur_user)
        self._check_student_id(payload.student_id)
        return self.lesson_repo.get_student_attendance_period(payload)

    def patch_attendance(self, attendance_id: int, payload: AttendancePatch, cur_user: dict) -> Dict[str, Any]:
        self._check_not_empty(payload)
        self._check_lesson_id(payload.lesson_id)
        self._check_student_id(payload.student_id)

        attendance = self.lesson_repo.get_attendance_by_id(attendance_id)
        if not attendance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такой записи посещаемости нет')
        self._check_lesson_owner(attendance['lesson_id'], cur_user)
        if payload.lesson_id:
            self._check_lesson_owner(payload.lesson_id, cur_user)

        return self.lesson_repo.patch_attendance(attendance_id, payload)

    def _check_not_empty(self, payload) -> None:
        if not payload.model_dump(exclude_unset=True):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Нет данных для обновления')

    def _check_course_owner(self, course_assignment_id: int, cur_user: dict) -> None:
        course = self.course_assignment_repo.get_course_assignment_by_id(course_assignment_id)
        check_course_owner(course['teacher_id'], cur_user)

    def _check_lesson_owner(self, lesson_id: int, cur_user: dict) -> Dict[str, Any]:
        lesson = self.lesson_repo.get_lesson_course(lesson_id)
        check_course_owner(lesson['teacher_id'], cur_user)
        return lesson

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
