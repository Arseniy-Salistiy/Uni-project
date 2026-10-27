from fastapi import Depends, APIRouter, HTTPException, status
from typing import List

from src.services.academic_performace_service import AcademicPerformanceService, get_academic_perf_service
from src.repository.academic_performace_repository import AcademicPerofrmaceRepository, get_academic_perf_repo
from src.schemas.academic_performace_schemas import *
from src.core.roles import Roles
from src.schemas.user_schemas import User
from src.core.auth import get_user
from src.core.config import settings

router = APIRouter(prefix='/performace', tags=['academic performace'])

@router.post('/assignments', response_model=Assignmnet)
def create_assignment(
    payload: CreateAssignment,
    service: AcademicPerformanceService = Depends(get_academic_perf_service),
    role_check: bool = Depends(Roles([settings.TEACHER])),
    cur_user: User = Depends(get_user)                     
):
    return service.create_assignment(dict(cur_user), payload)

@router.get('/assignments/{assignment_id}', response_model=Assignmnet)
def get_assignment(assignment_id: int,
                    academic_repo: AcademicPerofrmaceRepository = Depends(get_academic_perf_repo),
                    role_check: bool = Depends(Roles([settings.DEAN, settings.STUDENT, settings.TEACHER]))):
    assignment = academic_repo.get_assignment_by_id(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Такого задания нет')
    return assignment

@router.get('/assignments/course/{course_assignment_id}', response_model=List[Assignmnet])
def get_assignments_group(course_assignment_id: int,
                            service: AcademicPerformanceService = Depends(get_academic_perf_service),
                            role_check: bool = Depends(Roles([settings.DEAN, settings.STUDENT, settings.TEACHER]))):
    return service.get_all_assignments_group(course_assignment_id)

@router.delete('/assignments/{assignment_id}', response_model=Assignmnet)
def delete_assignment(assignment_id: int,
                        cur_user: User = Depends(get_user),
                        service: AcademicPerformanceService = Depends(get_academic_perf_service),
                        role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER]))):
    return service.delete_assignment(assignment_id, dict(cur_user))

@router.get('/grades/student/{student_id}/course/{course_id}', response_model=List[GradeDetailedResponse])
def get_grades_student_course(student_id: int, course_id: int,
                                role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN, settings.TEACHER])),
                                cur_user: User = Depends(get_user),
                                service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.get_grades_by_student_course(student_id, course_id, dict(cur_user))

@router.get('/grades/{grade_id}', response_model=GradeDetailedResponse)
def get_grade(grade_id: int,
                cur_user: User = Depends(get_user),
                role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN, settings.TEACHER])),
                service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.get_grade_by_id(grade_id, dict(cur_user))

@router.get('/final/grade/student/{student_id}/course/{course_id}', response_model=FinalGrade)
def get_final_grade(student_id: int, course_id: int,
                    cur_user: User = Depends(get_user),
                    role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN, settings.TEACHER])),
                    service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.get_final_grade_by_course(student_id, course_id, dict(cur_user))

@router.get('/students/{student_id}/gpa', response_model=StudentGpaResponse)
def get_student_gpa(student_id: int,
                    role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN, settings.TEACHER])),
                    cur_user: User = Depends(get_user),
                    service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.get_student_gpa(student_id, dict(cur_user))

@router.post('/grades', response_model=Grade)
def create_grade(payload: CreateGrade,
                cur_user: User = Depends(get_user),
                role_check: bool = Depends(Roles([settings.TEACHER])),
                service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.give_grade(dict(cur_user), payload)

@router.delete('/grades/{grade_id}', response_model=Grade)
def delete_grade(grade_id: int,
                cur_user: User = Depends(get_user),
                role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER])),
                service: AcademicPerformanceService = Depends(get_academic_perf_service)):
    return service.delete_grade(grade_id, dict(cur_user))