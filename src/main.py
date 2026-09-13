from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
import psycopg2

from src.db.database import get_db, init_pool, close_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()

app = FastAPI(lifespan=lifespan)

@app.get('/')
def test_endpoint():
    return "Hello"

@app.get('/test')
def fun(db: Annotated[psycopg2.extensions.connection, Depends(get_db)]):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM departments")
        rows = cur.fetchall()
    return {"result": rows}

@app.get('/health')
def health_check(db: Annotated[psycopg2.extensions.connection, Depends(get_db)]):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM majors")
        rows = cur.fetchall()
    return {"status": "db connected",
            "result": rows}