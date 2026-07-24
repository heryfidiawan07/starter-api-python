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
        nodes = {}
        for p in r.permissions:
            if p.type in ("category", "menu"):
                if p.id not in nodes:
                    nodes[p.id] = {
                        "id": p.id,
                        "label": p.label,
                        "name": p.name,
                        "type": p.type,
                        "icon": p.icon,
                        "route": p.route,
                        "actions": [],
                        "children": []
                    }

        permissions_tree = []
        for p in r.permissions:
            if p.type == "category":
                node = nodes.get(p.id)
                if node and node not in permissions_tree:
                    permissions_tree.append(node)
            elif p.type == "menu":
                if p.parent_id:
                    parent = nodes.get(p.parent_id)
                    node = nodes.get(p.id)
                    if parent and node and node not in parent["children"]:
                        parent["children"].append(node)
            elif p.type == "action":
                if p.parent_id:
                    parent = nodes.get(p.parent_id)
                    if parent:
                        action_node = {
                            "id": p.id,
                            "name": p.name,
                            "label": p.label,
                        }
                        if action_node not in parent["actions"]:
                            parent["actions"].append(action_node)

        d["permissions"] = permissions_tree

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
