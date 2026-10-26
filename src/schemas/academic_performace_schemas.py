from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field
from src.schemas.enums import AssignmentType

class CreateAssignment(BaseModel):
    course_assignment_id: int
    title: str
    type: AssignmentType = Field(default=AssignmentType.LAB)
    coefficient: Decimal = Field(default=Decimal(1.00), ge=Decimal(1.00), le=Decimal(99.99))
    max_grade: int = Field(default=5, ge=0, le=100)

class Assignmnet(CreateAssignment):
    id: int

class CreateGrade(BaseModel):
    student_id: int
    course_assignment_id: int
    assignment_id: None | int
    grade: int = Field(default=5, ge=0, le=5)
    graded_at: datetime = Field(default=datetime.now())
    submission_id: None | int
    is_final: None | bool = Field(default=False)

class Grade(CreateGrade):
    id: int
    graded_by: int

class GradeDetailedResponse(BaseModel):
    grade_id: int
    grade: float
    graded_at: datetime
    student_id: int
    student_fio: str
    course_assignment_id: int
    subject_id: int
    subject_name: str
    assignment_id: None | int
    assignment_title: None | str
    assignment_type: None | AssignmentType
    assignment_coefficient: None | Decimal = Field(default=Decimal(1.00), ge=Decimal(1.00), le=Decimal(99.99))
    teacher_id: None | int
    teacher_fio: None | str
    is_final: bool