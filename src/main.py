from typing import Annotated
from fastapi import FastAPI, Depends

from src.db.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI()

@app.get('/')
def test_endpoint():
    return "Hello"

@app.get('/health')
def health_check(db: Annotated[Session, Depends(get_db)]):
    a = db.execute(text('SELECT 1'))
    return {'status': 'db connected',
            'var': a}