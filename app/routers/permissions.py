from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import response as R
from ..deps import get_db, require_permission
from ..serializers import serialize_permission
from ..services import permission_service as svc

router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])


def _serialize_tree(p) -> dict:
    d = serialize_permission(p)
    children = getattr(p, "_children", [])
    if children:
        d["children"] = [_serialize_tree(c) for c in children]
    return d


@router.get("")
def index(
    _: dict = Depends(require_permission("permission:index")),
    db: Session = Depends(get_db),
):
    perms = svc.find_all(db)
    return R.ok("Permissions retrieved", [serialize_permission(p) for p in perms])


@router.get("/tree")
def tree(
    _: dict = Depends(require_permission("permission:index")),
    db: Session = Depends(get_db),
):
    roots = svc.find_tree(db)
    return R.ok("Permission tree retrieved", [_serialize_tree(r) for r in roots])


@router.get("/by-role/{role_id}")
def by_role(
    role_id: str,
    _: dict = Depends(require_permission("permission:index")),
    db: Session = Depends(get_db),
):
    perms = svc.find_by_role_id(role_id, db)
    return R.ok("Role permissions retrieved", [serialize_permission(p) for p in perms])
