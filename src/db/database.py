from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.core.config import settings

_pool = None

def init_pool():
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.POSTGRES_URL,
            cursor_factory=RealDictCursor,
        )

def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None

@contextmanager
def get_conn():
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)

def get_db():
    with get_conn() as conn:
        yield conn