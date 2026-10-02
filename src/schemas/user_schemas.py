import re
from datetime import date

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.enums import *

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone: str = Field(pattern=r"^(\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    password: str
    role_id: int

class CreateTeacher(CreateUser):
    department_id: int
    position: str
    degree: str

class CreateStudent(CreateUser):
    date_of_birth: date
    gender: Gender
    group_id: int
    funding_type: FundingType
    enrollment_date: date

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    phone: str = Field(pattern=r"^(\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    email: EmailStr
    role_id: int

    model_config = ConfigDict(from_attributes=True)

class TeacherPatch(BaseModel):
    department_id: None|int = Field(default=None, examples=[None])
    position: None|str = Field(default=None, examples=[None])
    degree: None|str = Field(default=None, examples=[None])

class StudentPatch(BaseModel):
    date_of_birth: date|None = Field(default=None, examples=[None])
    gender: None|Gender = Field(default=None, examples=[None])
    group_id: int|None = Field(default=None, examples=[None])
    funding_type: None|FundingType = Field(default=None, examples=[None])
    status: None|StudentStatus = Field(default=None, examples=[None])
    enrollment_date: None|date = Field(default=None, examples=[None])