from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import response as R
from ..deps import get_current_user, get_db
from ..models import Role
from ..serializers import serialize_permission
from ..services import permission_service as perm_svc

router = APIRouter(prefix="/api/v1/lookup", tags=["lookup"])


@router.get("/roles")
def get_roles(
    _: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roles = db.query(Role).filter(Role.deleted_at.is_(None)).order_by(Role.name).all()
    data = [{"id": r.id, "name": r.name} for r in roles]
    return R.ok("Roles retrieved", data)


@router.get("/permissions")
def get_permissions(
    _: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perms = perm_svc.find_all(db)
    return R.ok("Permissions retrieved", [serialize_permission(p) for p in perms])
