import psycopg2
from fastapi import Depends
from typing import Dict, Any, Optional

from src.db.database import get_db
from src.schemas.course_schemas import CreateCourseAssignment

class CourseAssignment:
    def __init__(self, conn):
        self.conn = conn

    def assign_course(self, data: CreateCourseAssignment) -> Dict[str, Any]:
        query = """
        INSERT INTO course_assignments (group_id, subject_id, teacher_id, term, academic_year)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING id, group_id, subject_id, teacher_id, term, academic_year
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (data.group_id, data.subject_id,
                                data.teacher_id, data.term,
                                data.academic_year))
            return cur.fetchone()

def get_course_assignment_repo(conn=Depends(get_db)) -> CourseAssignment:
    return CourseAssignment(conn)