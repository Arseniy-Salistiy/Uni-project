from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path
import time

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from yoyo import get_backend, read_migrations
import logging
import psycopg2

from src.db.database import get_db, init_pool, close_pool
from src.core.config import settings
from src.api import users, academic_process, students, teachers, dictionaries, admin_panel, academic_performance, analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    db_url = settings.POSTGRES_URL
    back = get_backend(db_url)
    cur_dir = Path(__file__).resolve().parent
    amp = cur_dir.parent / "migrations"
    migrations = read_migrations(str(amp))
    with back.lock():
        back.apply_migrations(back.to_apply(migrations))
    yield
    close_pool()

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"persistAuthorization": True})

@app.exception_handler(HTTPException)
def global_exception_handler(request, exc: HTTPException):
    logger.warning(
        f"Ошибка {exc.status_code} при {request.method} {request.url.path}"
        f"Причина {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "result": None,
            "error": {
                "message": exc.detail,
                "code": exc.status_code
            }
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",            
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)

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
app.include_router(admin_panel.router)
app.include_router(academic_performance.router)
app.include_router(analytics.router)