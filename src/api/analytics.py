from fastapi import Depends, APIRouter, Query
from typing import List

from src.services.analytics_service import AnalyticsService, get_analytics_service
from src.schemas.analytics_schemas import *
from src.core.roles import Roles
from src.schemas.user_schemas import User
from src.core.auth import get_user
from src.core.config import settings

router = APIRouter(prefix='/analytics', tags=['analytics'])

@router.get('/reports/group/{group_id}/subject/{subject_id}', response_model=List[GroupSubjectReport])
def get_group_subject_report(group_id: int, subject_id: int, is_final: bool = Query(default=False),
                             role_check: bool = Depends(Roles([settings.TEACHER, settings.DEAN])),
                             service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_group_subject_report(group_id, subject_id, is_final)

@router.get('/reports/student-summary/{student_id}', response_model=List[StudentSummaryReport])
def get_student_summary_report(student_id: int,
                               role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN])),
                               cur_user: User = Depends(get_user),
                               service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_student_summary_report(student_id, dict(cur_user))