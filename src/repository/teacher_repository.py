import psycopg2
from fastapi import Depends
from typing import Dict, Any

from src.schemas import CreateTeacher
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

def get_teacher_repo(conn=Depends(get_db)) -> TeacherRepository:
    return TeacherRepository(conn)