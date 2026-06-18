import math

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import response as R
from ..deps import get_db, require_permission
from ..schemas.role import CreateRoleRequest, UpdateRoleRequest
from ..serializers import serialize_role
from ..services import role_service as svc

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("")
def index(
    search: str = "",
    page: int = 1,
    per_page: int = 10,
    _: dict = Depends(require_permission("role:index")),
    db: Session = Depends(get_db),
):
    items, total = svc.find_all(db, search or None, page, per_page)
    meta = {"page": page, "per_page": per_page, "total": total, "total_page": math.ceil(total / per_page)}
    return R.ok_paged("Roles retrieved", [serialize_role(r) for r in items], meta)


@router.get("/{role_id}")
def show(
    role_id: str,
    _: dict = Depends(require_permission("role:show")),
    db: Session = Depends(get_db),
):
    return R.ok("Role retrieved", serialize_role(svc.find_by_id(role_id, db)))


@router.post("")
def create(
    req: CreateRoleRequest,
    _: dict = Depends(require_permission("role:create")),
    db: Session = Depends(get_db),
):
    return R.created("Role created", serialize_role(svc.create(req, db)))


@router.put("/{role_id}")
def update(
    role_id: str,
    req: UpdateRoleRequest,
    _: dict = Depends(require_permission("role:edit")),
    db: Session = Depends(get_db),
):
    return R.ok("Role updated", serialize_role(svc.update(role_id, req, db)))


@router.delete("/{role_id}")
def delete(
    role_id: str,
    _: dict = Depends(require_permission("role:delete")),
    db: Session = Depends(get_db),
):
    svc.delete(role_id, db)
    return R.ok("Role deleted")
