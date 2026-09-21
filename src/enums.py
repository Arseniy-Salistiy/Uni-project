from enum import Enum

class EducationForm(str, Enum):
    FULL_TIME = 'очное'
    PART_TIME = 'заочное'
    MIXED = 'очно-заочное'

class Gender(str, Enum):
    MALE = 'М'
    FEMALE = 'Ж'

class FundingType(str, Enum):
    BUDGET = 'бюджет'
    PAID = 'платное'

class StudentStatus(str, Enum):
    ACTIVE = "числится"
    ACADEMIC = "академический отпуск"
    EXPELLED = "отчислен"
    GRADUATED = "выпустился"