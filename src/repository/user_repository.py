import psycopg2
from fastapi import Depends
from typing import Dict, Any, Optional

from src.schemas import CreateUser
from src.core.auth import hash_password
from src.db.database import get_db

class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, password, role_id FROM users WHERE email = %s;"
        
        with self.conn.cursor() as cur:
            cur.execute(query, (email,))
            return cur.fetchone()

    def get_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, role_id FROM users WHERE phone = %s;"

        with self.conn.cursor() as cur:
            cur.execute(query, (phone,))
            return cur.fetchone()

    def create_user(self, credentials: CreateUser) -> Dict[str, Any]:
        query = """
        INSERT INTO users (first_name, last_name, middle_name, email, phone, password, role_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, first_name, last_name, middle_name, phone, email, role_id
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (
                            credentials.first_name,
                            credentials.last_name,
                            credentials.middle_name,
                            credentials.email,
                            credentials.phone,
                            hash_password(credentials.password),
                            credentials.role_id))
            return cur.fetchone()

def get_user_repo(conn=Depends(get_db)) -> UserRepository:
    return UserRepository(conn)