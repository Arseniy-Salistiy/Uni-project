import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.user_schemas import CreateStudent, StudentPatch

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

    def get_student_by_id(self, id: int) -> None | Dict[str, Any]:
        query = """SELECT
                    u.id, u.first_name, u.last_name, u.middle_name,
                    u.email, u.phone, s.date_of_birth, s.gender,
                    g.name as group_name, s.funding_type, s.status
                   FROM users as u
                   JOIN students as s ON s.user_id = u.id
                   JOIN groups as g ON g.id = s.group_id
                   WHERE u.id = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def update_student_info(self, student_id: int, payload: StudentPatch):
        data = {key: value for key, value in payload.model_dump().items() if value}

        if not data:
            return {}

        keys = ','.join([f'{i} = %s' for i in data.keys()])
        keys_for_returning = 'user_id,' + ','.join(data)
        query = f"""UPDATE students SET {keys} WHERE user_id=%s
                    RETURNING {keys_for_returning}"""

        with self.conn.cursor() as cur:
            cur.execute(query, (*data.values(), student_id,))
            return cur.fetchone()

def get_student_repo(conn=Depends(get_db)) -> StudentRepository:
    return StudentRepository(conn)