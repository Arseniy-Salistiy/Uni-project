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

class LessonType(str, Enum):
    LECTURE = "лекция"
    SEMINAR = "семинар"
    LAB = "лабораторная"
    WORKSHOP = "практика"

class LessonStatus(str, Enum):
    PRESENT = "присутствовал"
    ABSENT = "отсутствовал"
    LATE = "опоздал"
    EXCUSED = "уважительная причина"

class AssignmentType(str, Enum):
    LAB = "лабораторная"
    TEST = "контрольная"
    TERM_PAPER = "курсовая"
    ESSAY = "реферат"
    PROJECT = "проект"

class ControlForm(str, Enum):
    EXAM = "экзамен"
    TEST = "зачёт"
    TERM_PAPER = "курсовая"
    GRADED_TEST = "дифференцированный зачёт"