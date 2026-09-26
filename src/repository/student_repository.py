import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.user_schemas import CreateStudent

class StudentRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_student(self, user_id: int, payload: CreateStudent) -> Dict[str, Any]:
        query = """INSERT INTO students (user_id, date_of_birth, gender, group_id, funding_type, enrollment_date)
                    VALUES(%s, %s, %s, %s, %s, %s)
                    RETURNING user_id, gender, group_id, funding_type"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (user_id, payload.date_of_birth, payload.gender,
                                payload.group_id, payload.funding_type,
                                payload.enrollment_date))
            return cur.fetchone()

    def get_all_students(self) -> List[Dict[str, Any]]:
        query = """ SELECT
                     u.id, u.first_name, u.middle_name, u.last_name,
                     u.email, u.phone, s.gender, s.funding_type, s.status,
                     g.name
                    FROM users as u
                    JOIN students as s ON s.user_id = u.id
                    JOIN groups as g ON g.id = s.group_id
                    ORDER BY 2, 4
        """

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_student_repo(conn=Depends(get_db)) -> StudentRepository:
    return StudentRepository(conn)