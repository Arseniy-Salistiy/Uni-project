import psycopg2
from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db

class AdminPanelRepository:
    def __init__(self, conn):
        self.conn = conn

    def assign_role(self, id: int, new_role: int) -> Dict[str, Any]:
        query = """UPDATE users SET role_id = %s
                    WHERE id = %s
                    RETURNING *"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (new_role, id,))
            return cur.fetchone()

    def get_logs(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM audit_logs
                    OFFSET %s LIMIT %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (offset, limit,))
            return cur.fetchall()

    def acc_management(self):
        pass

def get_admin_panel_repo(conn=Depends(get_db)) -> AdminPanelRepository:
    return AdminPanelRepository(conn)