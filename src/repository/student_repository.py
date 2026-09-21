import psycopg2
from fastapi import Depends
from typing import Dict, Any

from src.db.database import get_db
from src.schemas import CreateStudent

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

def get_student_repo(conn=Depends(get_db)) -> StudentRepository:
    return StudentRepository(conn)