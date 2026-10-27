from fastapi import Depends, APIRouter, Query
from typing import List

from src.services.analytics_service import AnalyticsService, get_analytics_service
from src.schemas.analytics_schemas import *
from src.core.roles import Roles
from src.schemas.user_schemas import User
from src.core.auth import get_user
from src.schemas.enums import Type
from src.core.config import settings

router = APIRouter(prefix='/analytics', tags=['analytics'])

@router.get('/reports/group/{group_id}/subject/{subject_id}', response_model=List[GroupSubjectReport])
def get_group_subject_report(group_id: int, subject_id: int, is_final: bool = Query(default=False),
                             role_check: bool = Depends(Roles([settings.TEACHER, settings.DEAN])),
                             service: AnalyticsService = Depends(get_analytics_service)):
    """Ведомость по группе и дисциплине"""
    return service.get_group_subject_report(group_id, subject_id, is_final)

@router.get('/reports/student-summary/{student_id}', response_model=List[StudentSummaryReport])
def get_student_summary_report(student_id: int,
                               role_check: bool = Depends(Roles([settings.STUDENT, settings.DEAN])),
                               cur_user: User = Depends(get_user),
                               service: AnalyticsService = Depends(get_analytics_service)):
    """Сводная ведомость по студенту за весь период обучения"""
    return service.get_student_summary_report(student_id, dict(cur_user))

@router.get('/reports/group-rating/{group_id}', response_model=List[GroupRating])
def get_group_rating(group_id: int,
                     role_check: bool = Depends(Roles([settings.DEAN, settings.TEACHER, settings.STUDENT])),
                     service: AnalyticsService = Depends(get_analytics_service)):
    """Рейтинг студентов в группе по среднему баллу"""
    return service.get_group_rating(group_id)

@router.get('/reports/debtors', response_model=List[DebtorsReport])
def get_debtors_report(role_check: bool = Depends(Roles([settings.DEAN])),
                       service: AnalyticsService = Depends(get_analytics_service)):
    """Отчет по должникам"""
    return service.get_debtors_report()

@router.get('/reports/stats/{by_type}', response_model=List[AcademicStats])
def get_academic_stats(by_type: Type,
                       role_check: bool = Depends(Roles([settings.DEAN])),
                       service: AnalyticsService = Depends(get_analytics_service)):
    """Статистика успеваемости по группам, курсам, специальностям"""
    return service.get_academic_stats(by_type)

@router.get('/reports/quality-of-knowledge', response_model=List[QualityReport])
def get_quality_of_knowledge(role_check: bool = Depends(Roles([settings.DEAN])),
                             service: AnalyticsService = Depends(get_analytics_service)):
    """Отчет по качеству знаний (процент студентов с оценками '4' и '5')"""
    return service.get_quality_of_knowledge_report()