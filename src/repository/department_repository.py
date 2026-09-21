import psycopg2
from typing import List, Dict, Any
from fastapi import Depends

from src.db.database import get_db

class DepartmentRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_departments(self) -> List[Dict[str, Any]]:
        query = """SELECT * FROM departments ORDER BY id"""

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_department_repo(conn=Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(conn)