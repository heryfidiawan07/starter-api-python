from sqlalchemy.orm import Session

from ..models import Permission, Role, User
from ..schemas.role import CreateRoleRequest, UpdateRoleRequest


def find_all(db: Session, search: str | None, page: int, per_page: int):
    q = db.query(Role).filter(Role.deleted_at.is_(None))
    if search:
        q = q.filter(Role.name.contains(search) | Role.description.contains(search))
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def find_by_id(role_id: str, db: Session) -> Role:
    role = db.query(Role).filter(Role.id == role_id, Role.deleted_at.is_(None)).first()
    if not role:
        raise KeyError("Role not found")
    return role


def create(req: CreateRoleRequest, db: Session) -> Role:
    if db.query(Role).filter(Role.name == req.name, Role.deleted_at.is_(None)).first():
        raise ValueError("Role name already taken")
    role = Role(name=req.name, description=req.description)
    if req.permission_ids:
        role.permissions = db.query(Permission).filter(Permission.id.in_(req.permission_ids)).all()
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update(role_id: str, req: UpdateRoleRequest, db: Session) -> Role:
    role = find_by_id(role_id, db)
    if req.name and req.name != role.name:
        if db.query(Role).filter(Role.name == req.name, Role.deleted_at.is_(None)).first():
            raise ValueError("Role name already taken")
        role.name = req.name
    if req.description is not None:
        role.description = req.description
    if req.permission_ids is not None:
        role.permissions = db.query(Permission).filter(Permission.id.in_(req.permission_ids)).all()
    db.commit()
    db.refresh(role)
    return role


def delete(role_id: str, db: Session) -> None:
    role = find_by_id(role_id, db)
    if db.query(User).filter(User.role_id == role_id, User.deleted_at.is_(None)).count():
        raise ValueError("Cannot delete role that is assigned to users")
    from datetime import datetime
    role.deleted_at = datetime.utcnow()
    db.commit()
