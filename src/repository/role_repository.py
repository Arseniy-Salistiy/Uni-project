from fastapi import Depends
from typing import List, Dict, Any

from src.db.database import get_db

class RoleRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_roles(self) -> List[Dict[str, Any]]:
        query = """SELECT * FROM roles"""

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_roles_repo(conn=Depends(get_db)) -> RoleRepository:
    return RoleRepository(conn)