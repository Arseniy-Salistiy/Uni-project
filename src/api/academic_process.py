from fastapi import APIRouter, Depends, status

from src.services.course_service import get_course_assignment_service, CourseAssignmentService
from src.services.lessons_service import get_lessons_service, LessonsService
from src.schemas.lessons_schemas import *
from src.schemas.course_schemas import CreateCourseAssignment, CourseAssignmentSchema, CourseAssignmentPatch
from src.core.roles import Roles
from src.core.config import settings

router = APIRouter(prefix='/study', tags=['academic process'])

@router.post('/assignments', response_model=CourseAssignmentSchema, status_code=status.HTTP_201_CREATED)
def assign_course(
    payload: CreateCourseAssignment,
    service: CourseAssignmentService = Depends(get_course_assignment_service),
    role_check: bool = Depends(Roles([settings.DEAN, settings.ADMIN]))
):
    res = service.assign_course(payload)
    return res

@router.get('/group/assignments')
def get_assignments(
    group_id: int,
    service: CourseAssignmentService = Depends(get_course_assignment_service),
    role_check: bool = Depends(Roles([settings.ADMIN, settings.DEAN, settings.TEACHER]))
    ):
    res = service.get_assignments_for_group(group_id)
    return res

@router.patch('/assignments/{course_id}')
def update_course_assignment(course_id: int, payload: CourseAssignmentPatch,
                            role_check: bool = Depends(Roles([settings.ADMIN, settings.DEAN])),
                            service: CourseAssignmentService = Depends(get_course_assignment_service)):
    return service.patch_course_assignment(course_id, payload)

@router.delete('/assignments/{course_id}')
def delete_course_assignment(course_id: int,
                            role_check: bool = Depends(Roles([settings.ADMIN, settings.DEAN])),
                            service: CourseAssignmentService = Depends(get_course_assignment_service)):
    return service.delete_course_assignment(course_id)

@router.post('/lessons')
def create_lesson():
    pass

@router.get('/lessons/groups/{group_id}')
def get_lessons_group():
    pass

@router.get('/lessons/{lesson_id}')
def get_lesson_id():
    pass

@router.patch('/lessons/{lesson_id}')
def update_lesson():
    pass

@router.delete('/lessons/{lesson_id}')
def delete_lesson():
    pass

@router.post('/attendance')
def create_attendance():
    pass

@router.get('/attendance/students/{student_id}')
def get_attendance_student():
    pass

@router.get('/attendance')
def get_attendance_for_period():
    pass

@router.patch('/attendance/{attendance_id}')
def update_attendance():
    pass