import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.academic_performace_schemas import CreateAssignment, CreateGrade

class AnalyticsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_group_subject_report(self, group_id: int, subject_id: int, is_final: bool) -> List[Dict[str, Any]]:
        query = """SELECT
                        s.user_id as student_id,
                        CONCAT_WS(' ', u.first_name, u.middle_name, u.last_name) as student_fio,
                        cast(g.grade AS FLOAT) as grade
                    FROM students s
                    JOIN users as u ON u.id = s.user_id
                    LEFT JOIN course_assignments ca ON ca.group_id = s.group_id AND ca.subject_id = %s
                    JOIN grades g ON g.student_id = s.user_id AND g.course_assignment_id = ca.id AND g.is_final = %s
                    WHERE s.group_id=%s
                    ORDER BY student_fio"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (subject_id, is_final, group_id,))
            return cur.fetchall()
    
    def get_student_summary_report(self, student_id: int) -> List[Dict[str, Any]]:
        query = """SELECT 
                        sub.name as subject_name,
                        ca.term,
                        ca.academic_year,
                        g.grade::FLOAT as grade,
                        sub.control_form
                    FROM grades g
                    JOIN course_assignments ca ON g.course_assignment_id = ca.id
                    JOIN subjects sub ON ca.subject_id = sub.id
                    WHERE g.student_id = %s AND g.is_final = TRUE
                    ORDER BY ca.term, sub.name;"""

        with self.conn.cursor() as cur:
            cur.execute(query, (student_id,))
            return cur.fetchall()

    def get_group_rating(self, group_id: int) -> List[Dict[str, Any]]:
        query = """SELECT 
                        DENSE_RANK() OVER (ORDER BY AVG(g.grade) DESC NULLS LAST)::INT as rank,
                        u.last_name || ' ' || u.first_name || ' ' || u.middle_name as student_fio,
                        COALESCE(ROUND(AVG(g.grade), 2), 0.0)::FLOAT as avg_grade
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                    WHERE s.group_id = %s
                    GROUP BY u.id, u.last_name, u.first_name, u.middle_name
                    ORDER BY rank;"""
        with self.conn.cursor() as cur:
            cur.execute(query, (group_id,))
            return cur.fetchall()

    def get_debtors_report(self) -> List[Dict[str, Any]]:
        query = """SELECT 
                        u.last_name || ' ' || u.first_name || ' ' || u.middle_name as student_fio,
                        gr.name as group_name,
                        sub.name as subject_name,
                        g.grade::FLOAT as grade
                    FROM grades g
                    JOIN users u ON g.student_id = u.id
                    JOIN students s ON u.id = s.user_id
                    JOIN groups gr ON s.group_id = gr.id
                    JOIN course_assignments ca ON g.course_assignment_id = ca.id
                    JOIN subjects sub ON ca.subject_id = sub.id
                    WHERE g.is_final = TRUE AND g.grade < 3.0
                    ORDER BY gr.name, student_fio;"""
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_analytics_repo(conn=Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(conn)