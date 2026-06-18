from datetime import datetime

from sqlalchemy.orm import Session

from .models import Base, Permission, User
from .security import hash_password


def seed(db: Session) -> None:
    _seed_permissions(db)
    _seed_root_user(db)


def _save(db: Session, parent_id, label: str, name: str, type_: str, route) -> Permission:
    p = Permission(parent_id=parent_id, label=label, name=name, type=type_, route=route)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_permissions(db: Session) -> None:
    if db.query(Permission).count() > 0:
        return

    main = _save(db, None, "Main", "main", "category", None)
    settings_ = _save(db, None, "Settings", "settings", "category", None)

    _save(db, main.id, "Dashboard", "dashboard", "menu", "/dashboard")

    admin = _save(db, settings_.id, "Administrator", "administrator", "category", None)
    user_menu = _save(db, admin.id, "User", "user", "menu", "/settings/users")
    role_menu = _save(db, admin.id, "Role", "role", "menu", "/settings/roles")
    perm_menu = _save(db, admin.id, "Permission", "permission", "menu", "/settings/permissions")

    for action in ["index", "show", "create", "edit", "delete"]:
        _save(db, user_menu.id, action.capitalize(), f"user:{action}", "action", None)
        _save(db, role_menu.id, action.capitalize(), f"role:{action}", "action", None)

    _save(db, perm_menu.id, "Index", "permission:index", "action", None)


def _seed_root_user(db: Session) -> None:
    if db.query(User).filter(User.email == "root@example.com").first():
        return
    user = User(
        name="Root",
        email="root@example.com",
        username="root",
        password=hash_password("password"),
        is_root=True,
        is_active=True,
        email_verified=True,
    )
    db.add(user)
    db.commit()
