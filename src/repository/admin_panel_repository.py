import psycopg2
from fastapi import Depends
from typing import Dict, Any

from src.db.database import get_db

class AdminPanelRepository:
    def __init__(self, conn):
        self.conn = conn

    def assign_role(self):
        pass

    def get_logs(self):
        pass

    def acc_management(self):
        pass

def get_admin_panel_repo(conn=Depends(get_db)) -> AdminPanelRepository:
    return AdminPanelRepository(conn)