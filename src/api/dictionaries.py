from fastapi import APIRouter, Depends

from src.repository.department_repository import get_department_repo, DepartmentRepository
from src.repository.major_repository import get_major_repo, MajorRepository
from src.repository.role_repository import get_roles_repo, RoleRepository

router = APIRouter(prefix='/info', tags=['dictionaries'])

@router.get('/roles')
def get_roles(role_repo: RoleRepository = Depends(get_roles_repo)):
    return role_repo.get_all_roles()

@router.get('/departments')
def get_departments(dep_repo: DepartmentRepository = Depends(get_department_repo)):
    return dep_repo.get_all_departments()

@router.get('/majors')
def get_majors(major_repo: MajorRepository = Depends(get_major_repo)):
    return major_repo.get_all_majors()