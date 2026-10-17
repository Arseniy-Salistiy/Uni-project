import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.course_schemas import CreateCourseAssignment, CourseAssignmentPatch

class CourseAssignmentRepository:
    def __init__(self, conn):
        self.conn = conn

    def assign_course(self, data: CreateCourseAssignment, user_id: int) -> Dict[str, Any]:
        query = """
        INSERT INTO course_assignments (group_id, subject_id, teacher_id, term, academic_year)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING *
        """
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (data.group_id, data.subject_id,
                                data.teacher_id, data.term,
                                data.academic_year))
            return cur.fetchone()

    def update_course_assignment(self, course_id: int, user_id: int, payload: CourseAssignmentPatch) -> Dict[str, Any]:
        data = payload.model_dump(exclude_unset=True)

        if not data:
            return {}
        
        keys = ','.join([f'{i} = %s' for i in data.keys()])
        query = f"""UPDATE course_assignments SET {keys} WHERE id=%s
                    RETURNING *"""
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (*data.values(), course_id,))
            return cur.fetchone()

    def delete_course_assignment(self, course_assignment_id: int, user_id: int) -> Dict[str, Any]:
        query = """DELETE FROM course_assignments WHERE id=%s
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (course_assignment_id,))
            return cur.fetchone()

    def get_course_assignment_by_id(self, id: int) -> None | Dict[str, Any]:
        query = """SELECT * FROM course_assignments WHERE id=%s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def get_assignments_for_group(self, group_id: int) -> None | List[Dict[str, Any]]:
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