from fastapi import APIRouter, Depends, status

from src.services.course_service import get_course_assignment_service, CourseAssignmentService
from src.schemas.course_schemas import CreateCourseAssignment, CourseAssignmentSchema

router = APIRouter(prefix='/study', tags=['academic process'])

@router.post('/assign_course', response_model=CourseAssignmentSchema, status_code=status.HTTP_201_CREATED)
def assign_course(
    payload: CreateCourseAssignment,
    service: CourseAssignmentService = Depends(get_course_assignment_service)
):
    res = service.assign_course(payload)
    return res

@router.get('/group/assignments')
def get_assignments(
    group_id: int,
    service: CourseAssignmentService = Depends(get_course_assignment_service)
    ):
    res = service.get_assignments_for_group(group_id)
    return res

@router.patch('/update/{course_id}')
def update_course_assignment():
    pass

@router.delete('/delete/{course_id}')
def delete_course_assignment():
    pass