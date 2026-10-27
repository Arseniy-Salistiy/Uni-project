from pydantic import BaseModel, Field

from src.schemas.enums import ControlForm

class GroupSubjectReport(BaseModel):
    student_id: int
    student_fio: str
    grade: float

class StudentSummaryReport(BaseModel):
    subject_name: str
    term: int
    academic_year: str
    grade: float
    control_form: ControlForm