from fastapi import APIRouter, Depends, Query, Body

from src.services.admin_panel_service import AdminPanelService, get_admin_panel_service
from src.core.roles import Roles
from src.core.config import settings

router = APIRouter(prefix='/admin', tags=['admin panel'])

@router.get('/logs')
def get_logs_router(page: int = Query(default=1, ge=1), 
                    per_page: int = Query(default=10, ge=1, le=100),
                    role_check: bool = Depends(Roles([settings.ADMIN])),
                    service: AdminPanelService = Depends(get_admin_panel_service)):
    return service.get_logs(page, per_page)

@router.patch('/roles/{user_id}')
def assign_roles(user_id: int, new_role: int = Body(ge=1, le=4),
                role_check: bool = Depends(Roles([settings.ADMIN])),
                service: AdminPanelService = Depends(get_admin_panel_service)):
    return service.assign_role(user_id, new_role)

@router.post('/accounts')
def manage_accs():
    pass

#backup router