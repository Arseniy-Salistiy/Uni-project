"""
Удаляю триггер
"""

from yoyo import step

__depends__ = {'20261026_01_m35Af-view-grades'}

steps = [
    step("DROP TRIGGER IF EXISTS audit_students_trigger ON STUDENTS;")
]
