from pydantic import BaseModel, Field, ConfigDict

class CreateCourseAssignment(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    term: int = Field(ge=1, le=10)
    academic_year: str

class CourseAssignmentSchema(CreateCourseAssignment):
    id: int

    model_config = ConfigDict(from_attributes=True)

class CourseAssignmentPatch(BaseModel):
    group_id: int|None = Field(default=None, examples=[None])
    subject_id: int|None = Field(default=None, examples=[None])
    teacher_id: int|None = Field(default=None, examples=[None])
    term: int|None = Field(default=None, ge=1, le=10, examples=[None])
    academic_year: str|None = Field(default=None, examples=[None])