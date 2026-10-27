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
        query = """SELECT * FROM grades_view
                    WHERE student_id = %s AND course_assignment_id = %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id, course_assignment_id,))
            return cur.fetchall()

    def get_final_grade_student(self, student_id: int, course_assignment_id: int) -> Dict[str, Any]:
        query = """SELECT
                        g.student_id,
                        sub.name as subject,
                        ROUND(SUM(g.grade * a.coefficient) / SUM(a.coefficient))::NUMERIC(3, 1) as final_grade
                    FROM grades as g
                    JOIN assignments as a ON g.assignment_id = a.id
                    JOIN course_assignments as ca ON g.course_assignment_id = ca.id
                    JOIN subjects as sub ON ca.subject_id = sub.id
                    WHERE g.student_id = %s AND g.course_assignment_id = %s
                    AND g.is_final = false
                    GROUP BY g.student_id, sub.name"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id, course_assignment_id,))
            return cur.fetchone()

    def calculate_student_gpa(self, student_id: int) -> Dict[str, Any]:
        query = """SELECT 
                        s.user_id as student_id,
                        u.last_name || ' ' || u.first_name || ' ' || u.middle_name as student_fio,
                        COALESCE(ROUND(AVG(g.grade), 2), 0.0)::FLOAT as gpa
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                    WHERE s.user_id = %s
                    GROUP BY s.user_id, u.last_name, u.first_name, u.middle_name;"""
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id,))
            return cur.fetchone()

    def get_grades_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM grades_view
                    WHERE student_id = %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (student_id,))
            return cur.fetchall()

    def get_grade_by_id(self, grade_id: int) -> Dict[str, Any]:
        query = """SELECT * FROM grades_view
                    WHERE grade_id = %s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (grade_id,))
            return cur.fetchone()

    def give_grade(self, graded_by: int, payload: CreateGrade) -> Dict[str, Any]:
        query = """INSERT INTO grades (student_id, course_assignment_id, assignment_id, grade, graded_by, graded_at, is_final)
                    VALUES(%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """
        for_log = "SET LOCAL app.current_user_id=%s;"        
        
        with self.conn.cursor() as cur:
            cur.execute(for_log, (graded_by,))
            cur.execute(query, (payload.student_id, payload.course_assignment_id,
                                payload.assignment_id, payload.grade,
                                graded_by, payload.graded_at,
                                payload.is_final,))
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

    def check_grade(self, grade_id: int) -> bool:
        query = "SELECT 1 FROM grades WHERE id = %s"

        with self.conn.cursor() as cur:
            cur.execute(query, (grade_id,))
            return cur.fetchone() is not None

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