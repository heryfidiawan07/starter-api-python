from datetime import datetime, timedelta
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_access_token(user_id: str, is_root: bool) -> str:
    payload = {
        "user_id": user_id,
        "is_root": is_root,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_access_expire),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def generate_refresh_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_refresh_expire),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


ACCESS_EXPIRE_SECONDS: int = settings.jwt_access_expire * 60
REFRESH_EXPIRE_MINUTES: int = settings.jwt_refresh_expire
