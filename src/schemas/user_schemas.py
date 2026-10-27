import re
from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from src.schemas.enums import *

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone: str = Field(pattern=r"^(\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    password: str = Field(min_length=6)

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
    phone: str | None
    email: str | None
    role_id: int

class UserMe(User):
    role: str

class UserWithRole(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    email: str | None
    role_id: int
    role_name: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

    @field_validator('role', mode='before')
    @classmethod
    def convert_int_role_to_text(cls, v):
        if isinstance(v, int):
            try:
                return UserRole(v).get_role
            except ValueError:
                return "unknown"
        return v

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

class UserPatch(BaseModel):
    first_name: str|None = Field(default=None, examples=[None])
    last_name: str|None = Field(default=None, examples=[None])
    middle_name: str|None = Field(default=None, examples=[None])
    email: EmailStr|None = Field(default=None, examples=[None])
    phone: str|None = Field(default=None, examples=[None], pattern=r"^(\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    password: str|None = Field(default=None, examples=[None], min_length=6)

class InfoItem(BaseModel):
    id: int
    name: str