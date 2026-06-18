import math

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from .. import response as R
from ..deps import get_current_user, get_db, require_permission
from ..schemas.user import CreateUserRequest, UpdateProfileRequest, UpdateUserRequest
from ..serializers import serialize_user
from ..services import user_service as svc

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.get("/users")
def index(
    search: str = "",
    page: int = 1,
    per_page: int = 10,
    _: dict = Depends(require_permission("user:index")),
    db: Session = Depends(get_db),
):
    items, total = svc.find_all(db, search or None, page, per_page)
    meta = {"page": page, "per_page": per_page, "total": total, "total_page": math.ceil(total / per_page)}
    return R.ok_paged("Users retrieved", [serialize_user(u) for u in items], meta)


@router.get("/users/{user_id}")
def show(
    user_id: str,
    _: dict = Depends(require_permission("user:show")),
    db: Session = Depends(get_db),
):
    return R.ok("User retrieved", serialize_user(svc.find_by_id(user_id, db)))


@router.post("/users")
def create(
    req: CreateUserRequest,
    _: dict = Depends(require_permission("user:create")),
    db: Session = Depends(get_db),
):
    return R.created("User created", serialize_user(svc.create(req, db)))


@router.put("/users/{user_id}")
def update(
    user_id: str,
    req: UpdateUserRequest,
    _: dict = Depends(require_permission("user:edit")),
    db: Session = Depends(get_db),
):
    return R.ok("User updated", serialize_user(svc.update(user_id, req, db)))


@router.delete("/users/{user_id}")
def delete(
    user_id: str,
    _: dict = Depends(require_permission("user:delete")),
    db: Session = Depends(get_db),
):
    svc.delete(user_id, db)
    return R.ok("User deleted")


@router.get("/profile")
def profile(current: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return R.ok("Profile retrieved", serialize_user(svc.find_by_id(current["user_id"], db)))


@router.put("/profile")
def update_profile(
    req: UpdateProfileRequest,
    current: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return R.ok("Profile updated", serialize_user(svc.update_profile(current["user_id"], req, db)))


@router.post("/profile/photo")
async def update_photo(
    photo: UploadFile = File(...),
    current: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = await svc.update_photo(current["user_id"], photo, db)
    return R.ok("Photo updated", serialize_user(user))
