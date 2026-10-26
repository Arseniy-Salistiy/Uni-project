from fastapi import Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any

from src.repository.admin_panel_repository import AdminPanelRepository, get_admin_panel_repo
from src.repository.user_repository import UserRepository, get_user_repo
from src.db.database import get_db

class AdminPanelService:
    def __init__(self, conn):
        self.admin_repo = AdminPanelRepository(conn)
        self.user_repo = UserRepository(conn)

    def create_backup(self, background_tasks: BackgroundTasks) -> dict:
        background_tasks.add_task(self.admin_repo.create_backup)
        return {
            "status": "accepted",
            "message": "Процесс резервного копирования запущен. Файл формируется в папке backups автономно."
        }

    def get_logs(self, page: int, per_page: int) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        return self.admin_repo.get_logs(offset, per_page)
    
    def assign_role(self, id: int, new_role: int) -> Dict[str, Any]:
        user = self.user_repo.get_user_by_id(id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Пользователь не найден')
        if user.get('role_id') == 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='нельзя изменить роль админу')
        return self.admin_repo.assign_role(id, new_role)

    def _check_user_id(self, id: int) -> None:
        if not self.user_repo.get_user_by_id(id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Пользователь не найден')

def get_admin_panel_service(conn=Depends(get_db)) -> AdminPanelService:
    return AdminPanelService(conn)