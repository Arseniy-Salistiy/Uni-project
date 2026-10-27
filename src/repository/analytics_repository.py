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

    def get_academic_stats(self, by_type: str) -> List[Dict[str, Any]]:
        if by_type == 'Группа':
            query = """SELECT gr.name as category_name, COALESCE(ROUND(AVG(g.grade), 2), 0.0)::FLOAT as avg_grade
                       FROM groups gr JOIN students s ON s.group_id = gr.id JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                       GROUP BY gr.id, gr.name ORDER BY avg_grade DESC;"""
        elif by_type == 'Курс':
            query = """SELECT gr.year::TEXT as category_name, COALESCE(ROUND(AVG(g.grade), 2), 0.0)::FLOAT as avg_grade
                       FROM groups gr JOIN students s ON s.group_id = gr.id JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                       GROUP BY gr.year ORDER BY category_name;"""
        elif by_type == 'Специальность':
            query = """SELECT m.name as category_name, COALESCE(ROUND(AVG(g.grade), 2), 0.0)::FLOAT as avg_grade
                       FROM majors m JOIN groups gr ON gr.major_id = m.id JOIN students s ON s.group_id = gr.id JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                       GROUP BY m.id, m.name ORDER BY avg_grade DESC;"""
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_quality_of_knowledge_report(self) -> List[Dict[str, Any]]:
        query = """WITH student_min_grades AS (
                        SELECT s.user_id, s.group_id, MIN(g.grade) as min_grade
                        FROM students s
                        JOIN grades g ON g.student_id = s.user_id AND g.is_final = TRUE
                        GROUP BY s.user_id, s.group_id
                    )
                    SELECT 
                        gr.name as group_name,
                        ROUND(COUNT(CASE WHEN smg.min_grade >= 3.5 THEN 1 END) * 100.0 / NULLIF(COUNT(smg.user_id), 0), 2)::FLOAT as quality_percentage
                    FROM groups gr
                    LEFT JOIN student_min_grades smg ON gr.id = smg.group_id
                    GROUP BY gr.id, gr.name
                    ORDER BY quality_percentage DESC NULLS LAST;"""
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_analytics_repo(conn=Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(conn)