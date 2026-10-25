import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.academic_performace_schemas import CreateAssignment, CreateGrade

class AcademicPerofrmaceRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_assignments_group(self, course_assignment_id: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM assignments
                    WHERE course_assignment_id = %s
                """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (course_assignment_id,))
            return cur.fetchall()

    def get_assignment_by_id(self, id: int) -> Dict[str, Any]:
        query = """SELECT * FROM assignments
                    WHERE id = %s
                """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def create_assignment(self, user_id: int, payload: CreateAssignment) -> Dict[str, Any]:
        query = """INSERT INTO assignments (course_assignment_id, title, type, coefficient, max_grade)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (payload.course_assignment_id,
                                payload.title,
                                payload.type,
                                payload.coefficient,
                                payload.max_grade,))
            return cur.fetchone()

    def delete_assignment(self, assignment_id: int, user_id: int) -> Dict[str, Any]:
        query = """DELETE FROM assignments WHERE id=%s
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (assignment_id,))
            return cur.fetchone()

    def get_grades_by_student_course(self, student_id: int, course_assignment_id: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM grades
                    WHERE student_id = %s AND course_assignment_id = %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id, course_assignment_id,))
            return cur.fetchall()

    def get_grades_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM grades
                    WHERE student_id = %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id,))
            return cur.fetchall()

    def get_grade_by_id(self, grade_id: int) -> Dict[str, Any]:
        query = "SELECT * FROM grades WHERE id = %s"

        with self.conn.cursor() as cur:
            cur.execute(query, (grade_id,))
            return cur.fetchone()

    def give_grade(self, graded_by: int, payload: CreateGrade) -> Dict[str, Any]:
        query = """INSERT INTO grades (student_id, course_assignment_id, assignment_id, grade, graded_by, graded_at)
                    VALUES(%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"        
        
        with self.conn.cursor() as cur:
            cur.execute(for_log, (graded_by,))
            cur.execute(query, (payload.student_id, payload.course_assignment_id,
                                payload.assignment_id, payload.grade,
                                graded_by, payload.graded_at,))
            return cur.fetchone()

    def delete_grade(self, grade_id: int, user_id: int) -> Dict[str, Any]:
        query = """DELETE FROM grades WHERE id = %s
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (user_id,))
            cur.execute(query, (grade_id,))
            return cur.fetchone()

    def get_submission_by_id(self):
        pass

    def get_submission_by_assignment(self):
        pass

    def submit(self):
        pass

    def delete_submission(self):
        pass

def get_academic_perf_repo(conn=Depends(get_db)) -> AcademicPerofrmaceRepository:
    return AcademicPerofrmaceRepository(conn)