from pydantic import BaseModel, Field

class CreateCourseAssignment(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    term: int = Field(ge=1, le=10)
    academic_year: str