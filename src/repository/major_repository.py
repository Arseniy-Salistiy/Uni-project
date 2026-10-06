from fastapi import Depends
from typing import List, Any, Dict

from src.db.database import get_db

class MajorRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_majors(self) -> List[Dict[str, Any]]:
        query = """SELECT * FROM majors"""

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
            
def get_major_repo(conn=Depends(get_db)) -> MajorRepository:
    return MajorRepository(conn)