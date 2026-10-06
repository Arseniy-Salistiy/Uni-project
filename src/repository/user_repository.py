import psycopg2
from fastapi import Depends
import logging
from typing import Dict, Any, Optional

from src.schemas.user_schemas import CreateUser, UserPatch
from src.core.auth import hash_password
from src.db.database import get_db

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, email, password, role_id FROM users WHERE email = %s;"
        
        with self.conn.cursor() as cur:
            cur.execute(query, (email,))
            return cur.fetchone()

    def get_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, role_id FROM users WHERE phone = %s;"

        with self.conn.cursor() as cur:
            cur.execute(query, (phone,))
            return cur.fetchone()

    def change_profile_info(self, user_id: int, payload: UserPatch) -> Dict[str, Any]:
        data = payload.model_dump(exclude_unset=True)

        if not data:
            return {}

        if data.get('password'):
            data['password'] = hash_password(data['password'])

        keys = ','.join([f'{i} = %s' for i in data.keys()])
        keys_for_returning = 'id,' + ','.join(data)
        query = f"""UPDATE users SET {keys} WHERE id=%s
                    RETURNING {keys_for_returning}"""

        with self.conn.cursor() as cur:
            cur.execute(query, (*data.values(), user_id,))
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