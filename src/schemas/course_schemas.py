from pydantic import BaseModel, Field

class CreateCourseAssignment(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    term: int = Field(ge=1, le=10)
    academic_year: str

class CourseAssignmentSchema(CreateCourseAssignment):
    id: int

class CourseAssignmentGet(BaseModel):
    id: int
    group: str
    subject: str
    teacher_id: int
    teacher: str
    term: int
    academic_year: str

class CourseAssignmentPatch(BaseModel):
    group_id: int|None = Field(default=None, examples=[None])
    subject_id: int|None = Field(default=None, examples=[None])
    teacher_id: int|None = Field(default=None, examples=[None])
    term: int|None = Field(default=None, ge=1, le=10, examples=[None])
    academic_year: str|None = Field(default=None, examples=[None])