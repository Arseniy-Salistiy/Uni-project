import psycopg2
from fastapi import Depends
from typing import Dict, Any, Optional, List

from src.db.database import get_db
from src.schemas.course_schemas import CreateCourseAssignment

class CourseAssignmentRepository:
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

    def get_course_assignment_by_id(self, id: int):
        pass

    def get_assignments_for_group(self, group_id: int) -> List[Dict[str, Any]]:
        query = """SELECT 
                    g.name, s.name, ca.teacher_id,
                    ca.term, ca.academic_year
                   FROM course_assignments as ca
                   JOIN groups as g ON g.id = ca.group_id
                   JOIN subjects as s ON s.id = ca.subject_id
                   WHERE ca.group_id = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (group_id,))
            return cur.fetchall()

def get_course_assignment_repo(conn=Depends(get_db)) -> CourseAssignmentRepository:
    return CourseAssignmentRepository(conn)