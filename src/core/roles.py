from fastapi import Depends, HTTPException, status

from src.core.auth import get_user

class Roles:
    def __init__(self, permitted_roles: list[int]):
        self.permitted_roles = permitted_roles

    def __call__(self, cur_user: dict = Depends(get_user)):
        if cur_user.get('role_id') not in self.permitted_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Доступ запрещен')
        return True