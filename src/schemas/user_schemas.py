import re
from datetime import date

from pydantic import BaseModel, EmailStr, Field

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