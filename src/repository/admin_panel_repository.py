import psycopg2
import logging
import subprocess
import os
from fastapi import Depends
from datetime import datetime
from typing import Dict, Any, List

from src.db.database import get_db
from src.core.config import settings

logger = logging.getLogger("uvicorn.error")

class AdminPanelRepository:
    def __init__(self, conn):
        self.conn = conn
        self.host = settings.POSTGRES_HOST
        self.user = settings.POSTGRES_USER
        self.password = settings.POSTGRES_PASSWORD
        self.db_name = settings.POSTGRES_NAME
        self.backup_dir = "/app/backups"

    def create_backup(self) -> None:
        filename = f"backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.sql"
        filepath = os.path.join(self.backup_dir, filename)

        os.makedirs(self.backup_dir, exist_ok=True)

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password

        cmd = [
            "pg_dump",
            "-h", self.host,
            "-U", self.user,
            "-d", self.db_name,
            "-F", "c",
            "-f", filepath
        ]

        logger.info(f"Фоновый процесс: Старт резервного копирования в файл {filename}")
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
            logger.info(f"Фоновый процесс: Бэкап {filename} успешно сохранен на хост.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Критический сбой фонового бэкапа. Ошибка утилиты pg_dump: {e.stderr}")

    def assign_role(self, id: int, new_role: int, by_user: int) -> Dict[str, Any]:
        query = """UPDATE users SET role_id = %s
                    WHERE id = %s
                    RETURNING id, first_name, last_name, middle_name, phone, email, role_id"""
        for_log = "SET LOCAL app.current_user_id=%s;"

        with self.conn.cursor() as cur:
            cur.execute(for_log, (by_user,))
            cur.execute(query, (new_role, id,))
            return cur.fetchone()

    def get_logs(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        query = """SELECT * FROM audit_logs
                    ORDER BY created_at DESC, id DESC
                    OFFSET %s LIMIT %s"""
        
        with self.conn.cursor() as cur:
            cur.execute(query, (offset, limit,))
            return cur.fetchall()

    def acc_management(self):
        pass

def get_admin_panel_repo(conn=Depends(get_db)) -> AdminPanelRepository:
    return AdminPanelRepository(conn)