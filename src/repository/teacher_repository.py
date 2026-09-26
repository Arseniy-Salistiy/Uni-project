import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.schemas.user_schemas import CreateTeacher
from src.db.database import get_db

class TeacherRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_teacher(self, user_id: int, payload: CreateTeacher) -> Dict[str, Any]:
        query = """INSERT INTO teachers (user_id, department_id, position, degree)
                    VALUES(%s, %s, %s, %s)
                    RETURNING user_id, department_id, position, degree"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (user_id, payload.department_id,
                                payload.position, payload.degree,))
            return cur.fetchone()

    def get_all_teachers(self) -> List[Dict[str, Any]]:
        query = """ SELECT
                     u.id, u.first_name, u.middle_name, u.last_name,
                     u.email, u.phone, t.position, t.degree, d.name
                    FROM users as u
                    JOIN teachers as t ON t.user_id = u.id
                    JOIN departments as d ON d.id = t.department_id
                    ORDER BY 2, 4
        """

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_teacher_repo(conn=Depends(get_db)) -> TeacherRepository:
    return TeacherRepository(conn)