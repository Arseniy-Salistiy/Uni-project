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

class GroupRating(BaseModel):
    rank: int
    student_fio: str
    avg_grade: float

class DebtorsReport(BaseModel):
    student_fio: str
    group_name: str
    subject_name: str
    grade: float

class AcademicStats(BaseModel):
    category_name: str
    avg_grade: float

class QualityReport(BaseModel):
    group_name: str
    quality_percentage: float