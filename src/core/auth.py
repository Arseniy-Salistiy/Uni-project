from datetime import datetime, timezone, timedelta

import jwt
import psycopg2
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from src.core.config import settings
from src.db.database import get_db

password_hash = PasswordHash.recommended()
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_user(token: str = Depends(oauth2_scheme),
            db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM])

        email: str|None = payload.get('email')

        if email is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='У токена истек срок годности',
                            headers={"WWW-Authenticate": "Bearer"})

    except jwt.PyJWTError:
        raise credentials_exception

    query = """SELECT id, email, role_id FROM users WHERE email = %s"""

    with db.cursor() as cur:
        cur.execute(query, (email,))
        user = cur.fetchone()
        
    if user is None:
        raise credentials_exception

    return user