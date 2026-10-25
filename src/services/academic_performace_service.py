from fastapi import Depends, HTTPException, status
from typing import List, Dict, Any

from src.repository.academic_performace_repository import AcademicPerofrmaceRepository
from src.repository.course_assignment_repository import CourseAssignmentRepository
from src.repository.student_repository import StudentRepository
from src.schemas.academic_performace_schemas import CreateAssignment, CreateGrade
from src.db.database import get_db

class AcademicPerformanceService:
    def __init__(self, conn):
        self.academic_perf_repo = AcademicPerofrmaceRepository(conn)
        self.course_assignment_repo = CourseAssignmentRepository(conn)
        self.student_repo = StudentRepository(conn)

    def get_all_assignments_group(self, course_assignment_id: int) -> List[Dict[str, Any]]:
        self._check_course_assigment(course_assignment_id)
        return self.academic_perf_repo.get_all_assignments_group(course_assignment_id)

    def create_assignment(self, user_id: int, payload: CreateAssignment) -> Dict[str, Any]:
        self._check_course_assigment(payload.course_assignment_id)
        return self.academic_perf_repo.create_assignment(user_id, payload)

    def delete_assignment(self, assignment_id: int, user_id: int) -> Dict[str, Any]:
        self._check_assignment(assignment_id)
        return self.academic_perf_repo.delete_assignment(assignment_id, user_id)

    def get_grades_by_student_course(self, student_id: int, course_assignment_id: int) -> List[Dict[str, Any]]:
        self._check_student(student_id)
        self._check_course_assigment(course_assignment_id)
        return self.academic_perf_repo.get_grades_by_student_course(student_id, course_assignment_id)

    def get_gpa_student_by_course(self, student_id: int, course_id: int):
        all_grades = self.academic_perf_repo.get_grades_by_student_course(student_id, course_id)
        fetched_grades = [i['grade'] for i in all_grades]
        

    def give_grade(self, graded_by: int, payload: CreateGrade) -> Dict[str, Any]:
        self._check_assignment(payload.assignment_id)
        self._check_course_assigment(payload.course_assignment_id)
        self._check_student(payload.student_id)
        return self.academic_perf_repo.give_grade(graded_by, payload)

    def delete_grade(self, grade_id: int, user_id: int) -> Dict[str, Any]:
        self._check_grade(grade_id)
        return self.academic_perf_repo.delete_grade(grade_id, user_id)

    def _check_course_assigment(self, course_assignment_id: int) -> None:
        if not self.course_assignment_repo.get_course_assignment_by_id(course_assignment_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого назначения дисциплины нет')
    
    def _check_assignment(self, assignment_id: None | int) -> None:
        if not self.academic_perf_repo.get_assignment_by_id(assignment_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Такого задания нет')

    def _check_student(self, student_id: int) -> None:
        if not self.student_repo.get_student_by_id(student_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Студента не существует')

    def _check_grade(self, grade_id: int) -> None:
        if not self.academic_perf_repo.get_grade_by_id(grade_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Оценка не найдена')

def get_academic_perf_service(conn=Depends(get_db)) -> AcademicPerformanceService:
    return AcademicPerformanceService(conn)