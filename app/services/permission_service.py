from sqlalchemy.orm import Session

from ..models import Permission


def find_all(db: Session):
    return db.query(Permission).filter(Permission.deleted_at.is_(None)).order_by(Permission.order).all()


def find_tree(db: Session):
    perms = find_all(db)
    pmap = {p.id: p for p in perms}
    for p in perms:
        p._children = []
    roots = []
    for p in perms:
        if p.parent_id is None:
            roots.append(p)
        elif p.parent_id in pmap:
            pmap[p.parent_id]._children.append(p)
    return roots


def find_by_role_id(role_id: str, db: Session):
    from ..models import Role
    role = db.query(Role).filter(Role.id == role_id, Role.deleted_at.is_(None)).first()
    return role.permissions if role else []
