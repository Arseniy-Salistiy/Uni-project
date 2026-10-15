from fastapi import APIRouter, Depends, status, Query

from src.services.course_service import get_course_assignment_service, CourseAssignmentService
from src.services.lessons_service import get_lessons_service, LessonsService
from src.repository.lesson_repository import LessonsRepository, get_lesson_repo
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

@router.post('/lessons', response_model=Lesson)
def create_lesson(payload: CreateLesson,
                role_check: bool = Depends(Roles([settings.DEAN])),
                service: LessonsService = Depends(get_lessons_service)):
    return service.create_lesson(payload)

@router.get('/lessons/groups/{group_id}', response_model=list[Lesson])
def get_lessons_group(group_id: int, lesson_date: LessonDate = Query(),
                        role_check: bool = Depends(Roles([settings.STUDENT, settings.TEACHER, settings.DEAN])),
                        service: LessonsService = Depends(get_lessons_service)):
    return service.get_lessons_by_group(group_id, lesson_date)

@router.get('/lessons/{lesson_id}', response_model=Lesson)
def get_lesson_id(lesson_id: int,
                    repo: LessonsRepository = Depends(get_lesson_repo)):
    return repo.get_lesson_by_id(lesson_id)

@router.patch('/lessons/{lesson_id}', response_model=Lesson)
def update_lesson(lesson_id: int, payload: LessonPatch,
                    role_check: bool = Depends(Roles([settings.DEAN])),
                    service: LessonsService = Depends(get_lessons_service)):
    return service.update_lesson(lesson_id, payload)

@router.delete('/lessons/{lesson_id}', response_model=Lesson)
def delete_lesson(lesson_id: int,
                    role_check: bool = Depends(Roles([settings.DEAN])),
                    service: LessonsService = Depends(get_lessons_service)):
    return service.delete_lesson(lesson_id)

@router.post('/attendance', response_model=Attendance)
def create_attendance(payload: CreateAttendance,
                        role_check: bool = Depends(Roles([settings.TEACHER])),
                        service: LessonsService = Depends(get_lessons_service)):
    return service.mark_attendance(payload)

@router.get('/attendance/students/{student_id}/course/{course_id}', response_model=list[Attendance])
def get_attendance_student(student_id: int, course_id: int, timeline: StudentDate = Depends(),
                            filter: AttendanceFilter = Depends(),
                            role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER])),
                            service: LessonsService = Depends(get_lessons_service)):
    return service.get_attendance_by_student(course_id, student_id, timeline, filter)

@router.get('/attendance', response_model=list[Attendance])
def get_attendance_for_period(payload: AttendancePeriod = Query(),
                                role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER])),
                                service: LessonsService = Depends(get_lessons_service)):
    return service.get_student_attendance_period(payload)

@router.patch('/attendance/{attendance_id}', response_model=Attendance)
def update_attendance(attendance_id: int, payload: AttendancePatch,
                        role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER])),
                        service: LessonsService = Depends(get_lessons_service)):
    return service.patch_attendance(attendance_id, payload)

