from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from .. import upload as upload_util
from ..models import Role, User
from ..schemas.user import CreateUserRequest, UpdateProfileRequest, UpdateUserRequest
from ..security import hash_password


def find_all(db: Session, search: str | None, page: int, per_page: int):
    q = db.query(User).filter(User.deleted_at.is_(None))
    if search:
        q = q.filter(
            User.name.contains(search) | User.email.contains(search) | User.username.contains(search)
        )
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def find_by_id(user_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise KeyError("User not found")
    return user


def create(req: CreateUserRequest, db: Session) -> User:
    if db.query(User).filter(User.email == req.email, User.deleted_at.is_(None)).first():
        raise ValueError("Email already taken")
    if db.query(User).filter(User.username == req.username, User.deleted_at.is_(None)).first():
        raise ValueError("Username already taken")
    if req.role_id and not db.query(Role).filter(Role.id == req.role_id, Role.deleted_at.is_(None)).first():
        raise KeyError("Role not found")

    user = User(
        name=req.name, email=req.email, username=req.username,
        password=hash_password(req.password),
        role_id=req.role_id, is_root=False, is_active=True, email_verified=True, verified_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(user_id: str, req: UpdateUserRequest, db: Session) -> User:
    user = find_by_id(user_id, db)
    if req.name is not None:
        user.name = req.name
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.role_id is not None:
        user.role_id = req.role_id if req.role_id else None
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def delete(user_id: str, db: Session) -> None:
    user = find_by_id(user_id, db)
    user.deleted_at = datetime.utcnow()
    db.commit()


def update_profile(user_id: str, req: UpdateProfileRequest, db: Session) -> User:
    user = find_by_id(user_id, db)
    if req.name:
        user.name = req.name
    if req.username:
        if req.username != user.username:
            if db.query(User).filter(User.username == req.username, User.deleted_at.is_(None)).first():
                raise ValueError("Username already taken")
        user.username = req.username
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


async def update_photo(user_id: str, file: UploadFile, db: Session) -> User:
    user = find_by_id(user_id, db)
    old_photo = user.photo
    user.photo = await upload_util.save_photo(file)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    if old_photo:
        upload_util.delete_photo(old_photo)
    return user
