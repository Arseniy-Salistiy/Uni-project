from fastapi import APIRouter, Depends
from typing import List

from src.repository.department_repository import get_department_repo, DepartmentRepository
from src.repository.major_repository import get_major_repo, MajorRepository
from src.repository.role_repository import get_roles_repo, RoleRepository
from src.repository.group_repository import get_group_repo, GroupRepository
from src.repository.subject_repository import get_subject_repo, SubjectRepository
from src.core.roles import Roles
from src.core.config import settings
from src.schemas.user_schemas import InfoItem

router = APIRouter(prefix='/info', tags=['dictionaries'])

@router.get('/roles', response_model=List[InfoItem])
def get_roles(role_repo: RoleRepository = Depends(get_roles_repo),
                role_check: bool = Depends(Roles([settings.DEAN, settings.ADMIN]))):
    return role_repo.get_all_roles()

@router.get('/departments', response_model=List[InfoItem])
def get_departments(dep_repo: DepartmentRepository = Depends(get_department_repo),
                    role_check: bool = Depends(Roles([settings.DEAN, settings.ADMIN, settings.STUDENT, settings.TEACHER]))):
    return dep_repo.get_all_departments()

@router.get('/majors', response_model=List[InfoItem])
def get_majors(major_repo: MajorRepository = Depends(get_major_repo),
                role_check: bool = Depends(Roles([settings.DEAN, settings.ADMIN, settings.STUDENT, settings.TEACHER]))):
    return major_repo.get_all_majors()

@router.get('/groups', response_model=List[InfoItem])
def get_groups(group_repo: GroupRepository = Depends(get_group_repo)):
    return group_repo.get_all_groups()

@router.get('/subjects', response_model=List[InfoItem])
def get_subjects(subject_repo: SubjectRepository = Depends(get_subject_repo),
                role_check: bool = Depends(Roles([settings.DEAN, settings.ADMIN, settings.STUDENT, settings.TEACHER]))):
    return subject_repo.get_all_subjects()