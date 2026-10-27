from pydantic import BaseModel, Field, model_validator

from datetime import date, time

from src.schemas.enums import LessonType, LessonStatus

class CreateLesson(BaseModel):
    course_assignment_id: int
    lesson_type: LessonType = Field(default=LessonType.LECTURE, examples=[LessonType.LECTURE])
    lesson_date: date = Field(default_factory=date.today, examples=[date.today()])
    start_time: time = Field(default=time(9, 0, 0), examples=[time(9, 0, 0)])
    end_time: time = Field(default=time(10, 30, 0), examples=[time(10, 30, 0)])
    room: str

    @model_validator(mode='after')
    def time_check(self):
        if self.end_time < self.start_time:
            raise ValueError('Время конца заняти не может быть меньше времени начала')
        if self.lesson_date < date.today():
            raise ValueError('Нельза назначить занятие задним числом')
        return self

class LessonDate(BaseModel):
    start_date: date = Field(default_factory=date.today, examples=[date.today()])
    end_date: date = Field(default_factory=date.today, examples=[date.today()])

    @model_validator(mode='after')
    def extra_check(self):
        if self.end_date < self.start_date:
            raise ValueError('конечная дата не может быть раньше начальной')
        return self

class LessonPatch(BaseModel):
    course_assignment_id: None|int = Field(default=None, examples=[None])
    lesson_type: None|LessonType = Field(default=None, examples=[LessonType.LECTURE])
    lesson_date: None|date = Field(default=None, examples=[date.today()])
    start_time: None|time = Field(default=None, examples=[time(9, 0, 0)])
    end_time: None|time = Field(default=None, examples=[time(10, 30, 0)])
    room: None|str = Field(default=None, examples=[None])

    @model_validator(mode='after')
    def time_check(self):
        if (self.start_time and not self.end_time) or (not self.start_time and self.end_time):
            raise ValueError('Введите время конца и начала занятия')
        if (self.end_time and self.start_time) and self.end_time < self.start_time:
            raise ValueError('Время конца заняти не может быть меньше времени начала')
        if self.lesson_date and self.lesson_date < date.today():
            raise ValueError('Нельза назначить занятие задним числом')
        return self

class Lesson(CreateLesson):
    id: int

class LessonGet(BaseModel):
    id: int
    group: str
    subject: str
    teacher: str
    lesson_type: LessonType
    lesson_date: date
    start_time: time
    end_time: time
    room: str

class CreateAttendance(BaseModel):
    lesson_id: int
    student_id: int
    status: LessonStatus = Field(default=LessonStatus.PRESENT, examples=[LessonStatus.PRESENT])

class AttendancePatch(BaseModel):
    lesson_id: None|int = Field(default=None, examples=[None])
    student_id: None|int = Field(default=None, examples=[None])
    status: None|LessonStatus = Field(default=LessonStatus.PRESENT, examples=[LessonStatus.PRESENT])

class AttendancePeriod(BaseModel):
    student_id: int
    start_date: date = Field(default_factory=date.today, examples=[date.today()])
    end_date: date = Field(default_factory=date.today, examples=[date.today()])

    @model_validator(mode='after')
    def date_check(self):
        if self.end_date < self.start_date:
            raise ValueError('Вторая дата не может быть меньше первой')
        return self

class StudentDate(BaseModel):
    start_date: None|date = Field(default=None, examples=[None])
    end_date: None|date = Field(default=None, examples=[None])

    @model_validator(mode='after')
    def extra_check(self):
        if (not self.start_date and self.end_date) or (self.start_date and not self.end_date):
            raise ValueError('Введите обе даты')
        if (self.start_date and self.end_date) and self.end_date < self.start_date:
            raise ValueError('конечная дата не может быть раньше начальной')
        return self

class AttendanceFilter(BaseModel):
    status: LessonStatus = Field(default=LessonStatus.PRESENT, examples=[LessonStatus.PRESENT])

class Attendance(CreateAttendance):
    id: int