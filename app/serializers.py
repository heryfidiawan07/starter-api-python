from typing import Any

from . import upload


def _dt(v) -> str | None:
    return v.isoformat() if v else None


def serialize_permission(p, include_children: bool = False) -> dict:
    d: dict[str, Any] = {
        "id": p.id,
        "parent_id": p.parent_id,
        "name": p.name,
        "label": p.label,
        "type": p.type,
        "route": p.route,
        "icon": p.icon,
        "order": p.order,
        "created_at": _dt(p.created_at),
        "updated_at": _dt(p.updated_at),
    }
    if include_children and hasattr(p, "_children"):
        d["children"] = [serialize_permission(c, include_children=True) for c in p._children]
    return d


def serialize_role(r) -> dict:
    d: dict[str, Any] = {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "created_at": _dt(r.created_at),
        "updated_at": _dt(r.updated_at),
    }
    if r.permissions is not None:
        d["permissions"] = [serialize_permission(p) for p in r.permissions]
    return d


def serialize_user(u) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "username": u.username,
        "photo": upload.build_photo_url(u.photo),
        "is_root": u.is_root,
        "is_active": u.is_active,
        "email_verified": u.email_verified,
        "role": serialize_role(u.role) if u.role else None,
        "created_at": _dt(u.created_at),
        "updated_at": _dt(u.updated_at),
    }
