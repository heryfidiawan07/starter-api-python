from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload["user_id"]
        is_root: bool = payload.get("is_root", False)
        return {"user_id": user_id, "is_root": is_root}
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="Unauthorized")


def require_permission(permission: str):
    def checker(
        current: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        if current["is_root"]:
            return current
        user = (
            db.query(User)
            .filter(User.id == current["user_id"], User.deleted_at.is_(None))
            .first()
        )
        if not user or not user.role:
            raise HTTPException(status_code=403, detail="Forbidden")
        has_perm = any(p.name == permission for p in (user.role.permissions or []))
        if not has_perm:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current

    return checker
