import psycopg2
from fastapi import Depends
from typing import Dict, Any

from src.db.database import get_db

class SubjectRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_subject_by_id(self, id: int) -> Dict[str, Any]:
        query = """SELECT id, name FROM subjects WHERE id = %s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

def get_subject_repo(conn=Depends(get_db)) -> SubjectRepository:
    return SubjectRepository(conn)