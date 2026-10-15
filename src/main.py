from contextlib import asynccontextmanager
from typing import Annotated
import time

from fastapi import FastAPI, Depends, Request
import logging
import psycopg2

from src.db.database import get_db, init_pool, close_pool
from src.api import users, academic_process, students, teachers, dictionaries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"persistAuthorization": True})

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    exec_time = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(exec_time)
    return response

@app.get('/health')
def health_check(db: Annotated[psycopg2.extensions.connection, Depends(get_db)]):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM majors")
        rows = cur.fetchall()
    return {"status": "db connected",
            "result": rows}

app.include_router(users.router)
app.include_router(academic_process.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(dictionaries.router)