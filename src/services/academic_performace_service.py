from fastapi import Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from typing import List, Dict, Any

from src.repository.academic_performace_repository import AcademicPerofrmaceRepository
from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.student_repository import StudentRepository
from src.schemas.academic_performace_schemas import CreateAssignment, CreateGrade
from src.core.config import settings
from src.core.roles import check_course_owner
from src.db.database import get_db

class AcademicPerformanceService:
    def __init__(self, conn):
        self.academic_perf_repo = AcademicPerofrmaceRepository(conn)
        self.course_assignment_repo = CourseAssignmentRepository(conn)
        self.student_repo = StudentRepository(conn)

    def get_all_assignments_group(self, course_assignment_id: int) -> List[Dict[str, Any]]:
        self._check_course_assigment(course_assignment_id)
        return self.academic_perf_repo.get_all_assignments_group(course_assignment_id)

    def create_assignment(self, cur_user: dict, payload: CreateAssignment) -> Dict[str, Any]:
        course = self._check_course_assigment(payload.course_assignment_id)
        check_course_owner(course['teacher_id'], cur_user)
        created = self.academic_perf_repo.create_assignment(cur_user['id'], payload)
        return self.academic_perf_repo.get_assignment_by_id(created['id'])

    def delete_assignment(self, assignment_id: int, cur_user: dict) -> Dict[str, Any]:
        assignment = self._check_assignment(assignment_id)
        course = self._check_course_assigment(assignment['course_assignment_id'])
        check_course_owner(course['teacher_id'], cur_user)
        self.academic_perf_repo.delete_assignment(assignment_id, cur_user['id'])
        return assignment

    def get_grades_by_student_course(self, student_id: int, course_assignment_id: int, cur_user: dict) -> List[Dict[str, Any]]:
        if cur_user.get('role_id') == settings.STUDENT:
            if student_id != cur_user.get('id'):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail='Нельзя смотреть чужие оценки')
        self._check_student(student_id)
        self._check_course_assigment(course_assignment_id)
        return self.academic_perf_repo.get_grades_by_student_course(student_id, course_assignment_id)

    def get_grade_by_id(self, grade_id: int, cur_user: dict) -> Dict[str, Any]:
        self._check_grade(grade_id)
        grade = self.academic_perf_repo.get_grade_by_id(grade_id)
        if cur_user.get('role_id') == settings.STUDENT:
            if grade.get('student_id') != cur_user.get('id'):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail='Нельзя смотреть чужие оценки')
        return grade
    
    def get_final_grade_by_course(self, student_id: int, course_id: int, cur_user: dict) -> Dict[str, Any]:
        self._check_course_assigment(course_id)
        self._check_student(student_id)
        if cur_user.get('role_id') == settings.STUDENT:
            if student_id != cur_user.get('id'):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail='Нельзя смотреть чужие оценки')
        final = self.academic_perf_repo.get_final_grade_student(student_id, course_id)
        if final is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='По дисциплине ещё нет оценок')
        return final

    def get_student_gpa(self, student_id: int, cur_user: dict) -> Dict[str, Any]:
        if cur_user.get('role_id') == settings.STUDENT and student_id != cur_user.get('id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя смотреть чужой GPA')
        self._check_student(student_id)
        return self.academic_perf_repo.calculate_student_gpa(student_id)
        
    def give_grade(self, cur_user: dict, payload: CreateGrade) -> Dict[str, Any]:
        course = self._check_course_assigment(payload.course_assignment_id)
        check_course_owner(course['teacher_id'], cur_user)
        if payload.assignment_id is not None:
            assignment = self._check_assignment(payload.assignment_id)
            if assignment['course_assignment_id'] != payload.course_assignment_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Задание относится к другой дисциплине')
        self._check_student(payload.student_id)
        if self.student_repo.get_student_by_id(payload.student_id)['group_id'] != course['group_id']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Студент не учится в группе, которой назначена дисциплина')
        try:
            return self.academic_perf_repo.give_grade(cur_user['id'], payload)
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Оценка уже выставлена')

    def delete_grade(self, grade_id: int, cur_user: dict) -> Dict[str, Any]:
        self._check_grade(grade_id)
        grade = self.academic_perf_repo.get_grade_by_id(grade_id)
        course = self._check_course_assigment(grade['course_assignment_id'])
        check_course_owner(course['teacher_id'], cur_user)
        return self.academic_perf_repo.delete_grade(grade_id, cur_user['id'])

    def _check_course_assigment(self, course_assignment_id: int) -> Dict[str, Any]:
        course = self.course_assignment_repo.get_course_assignment_by_id(course_assignment_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого назначения дисциплины нет')
        return course
    
    def _check_assignment(self, assignment_id: None | int) -> Dict[str, Any]:
        assignment = self.academic_perf_repo.get_assignment_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого задания нет')
        return assignment

    def _check_student(self, student_id: int) -> None:
        if not self.student_repo.get_student_by_id(student_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Студента не существует')

    def _check_grade(self, grade_id: int) -> None:
        if not self.academic_perf_repo.check_grade(grade_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Оценка не найдена')

def get_academic_perf_service(conn=Depends(get_db)) -> AcademicPerformanceService:
    return AcademicPerformanceService(conn)