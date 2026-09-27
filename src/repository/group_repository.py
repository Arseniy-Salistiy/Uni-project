import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db

class GroupRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_group_by_id(self, id: int) -> Dict[str, Any]:
        query = """SELECT id, name FROM groups WHERE id = %s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def get_all_groups(self) -> List[Dict[str, Any]]:
        query = """SELECT id, name FROM groups ORDER BY id"""

        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_group_repo(conn=Depends(get_db)) -> GroupRepository:
    return GroupRepository(conn)