"""
New column grade
"""

from yoyo import step

__depends__ = {'20261024_01_NbLQs-change-grades'}

steps = [
    step("ALTER TABLE GRADES ADD COLUMN IS_FINAL BOOLEAN NOT NULL DEFAULT FALSE;")
]
