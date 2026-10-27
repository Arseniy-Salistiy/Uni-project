from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.user_schemas import User, UserMe, UserPatch, LoginResponse
from src.services.user_service import get_user_service, UserService
from src.core.roles import Roles, ALL_ROLES
from src.schemas.enums import UserRole
from src.core.config import settings
from src.core.auth import *

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=UserMe)
def get_myself(current_user: User = Depends(get_user)):
    user = dict(current_user)
    try:
        user['role'] = UserRole(user['role_id']).get_role
    except ValueError:
        user['role'] = 'unknown'
    return user

@router.patch('/me', response_model=User)
def update_user_profile(payload: UserPatch, current_user: User = Depends(get_user),
                        role_check: bool = Depends(Roles(ALL_ROLES)),
                        service: UserService = Depends(get_user_service)):
    return service.patch_user_info(dict(current_user)['id'], payload)

@router.post('/login', response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
    user = service.fetch_user(form_data.username)
    if not user or not verify_password(form_data.password, user.get('password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверный пароль или email',
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token({"sub": user.get('email'), "role": user.get('role_id'), "id": user.get('id')})
    return {"access_token": access_token,
            "token_type": "bearer",
            "role": user.get('role_id')}

@router.post('/logout')
def logout():
    pass