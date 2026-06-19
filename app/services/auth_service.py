from datetime import datetime, timedelta
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from .. import mail as mail_service
from ..config import settings
from ..models import PasswordResetToken, RefreshToken, SocialAccount, User
from ..schemas.auth import (
    ChangePasswordRequest, ForgotPasswordRequest, LoginRequest,
    OAuthRequest, RefreshTokenRequest, RegisterRequest,
    ResetPasswordRequest, RevokeTokenRequest,
)
from ..security import (
    ACCESS_EXPIRE_SECONDS, REFRESH_EXPIRE_MINUTES,
    generate_access_token, generate_refresh_token, hash_password, verify_password,
)


def _token_pair(user: User, db: Session) -> dict:
    access_token = generate_access_token(user.id, user.is_root)
    refresh_token_value = generate_refresh_token(user.id)
    rt = RefreshToken(
        user_id=user.id,
        token=refresh_token_value,
        expires_at=datetime.utcnow() + timedelta(minutes=REFRESH_EXPIRE_MINUTES),
    )
    db.add(rt)
    db.commit()
    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "expires_in": ACCESS_EXPIRE_SECONDS,
    }


def register(req: RegisterRequest, db: Session) -> User:
    if db.query(User).filter(User.email == req.email, User.deleted_at.is_(None)).first():
        raise ValueError("Email already taken")
    if db.query(User).filter(User.username == req.username, User.deleted_at.is_(None)).first():
        raise ValueError("Username already taken")

    user = User(
        name=req.name, email=req.email, username=req.username,
        password=hash_password(req.password),
        is_root=False, is_active=True,
        email_verified=not settings.email_verification_required,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if settings.email_verification_required:
        vt = PasswordResetToken(
            user_id=user.id, token=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(vt)
        db.commit()
        mail_service.send_verification_email(user.email, user.name, vt.token)

    return user


def login(req: LoginRequest, db: Session) -> dict:
    user = db.query(User).filter(User.email == req.email, User.deleted_at.is_(None)).first()
    if not user or not verify_password(req.password, user.password):
        raise ValueError("Invalid credentials")
    if not user.is_active:
        raise ValueError("Account is inactive")
    if settings.email_verification_required and not user.email_verified:
        raise ValueError("Email not verified")
    return _token_pair(user, db)


def logout(user_id: str, db: Session) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).update({"revoked_at": datetime.utcnow()})
    db.commit()


def refresh(req: RefreshTokenRequest, db: Session) -> dict:
    rt = db.query(RefreshToken).filter(RefreshToken.token == req.refresh_token).first()
    if not rt or not rt.is_valid():
        raise ValueError("Invalid or expired refresh token")
    user = db.query(User).filter(User.id == rt.user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise ValueError("User not found")
    rt.revoked_at = datetime.utcnow()
    db.commit()
    result = _token_pair(user, db)
    result.pop("user")
    return result


def revoke_token(user_id: str, req: RevokeTokenRequest, db: Session) -> None:
    rt = db.query(RefreshToken).filter(RefreshToken.token == req.refresh_token).first()
    if not rt or rt.user_id != user_id:
        raise ValueError("Token not found")
    rt.revoked_at = datetime.utcnow()
    db.commit()


def forgot_password(req: ForgotPasswordRequest, db: Session) -> None:
    user = db.query(User).filter(User.email == req.email, User.deleted_at.is_(None)).first()
    if not user:
        return
    prt = PasswordResetToken(
        user_id=user.id, token=str(uuid4()),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(prt)
    db.commit()
    mail_service.send_password_reset_email(user.email, user.name, prt.token)


def reset_password(req: ResetPasswordRequest, db: Session) -> None:
    prt = db.query(PasswordResetToken).filter(PasswordResetToken.token == req.token).first()
    if not prt or not prt.is_valid():
        raise ValueError("Invalid or expired token")
    user = db.query(User).filter(User.id == prt.user_id).first()
    if not user:
        raise ValueError("User not found")
    user.password = hash_password(req.new_password)
    prt.used_at = datetime.utcnow()
    db.commit()


def verify_email(token: str, db: Session) -> None:
    vt = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not vt or not vt.is_valid():
        raise ValueError("Invalid or expired verification token")
    user = db.query(User).filter(User.id == vt.user_id).first()
    if not user:
        raise ValueError("User not found")
    user.email_verified = True
    vt.used_at = datetime.utcnow()
    db.commit()


def change_password(user_id: str, req: ChangePasswordRequest, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise ValueError("User not found")
    if not verify_password(req.current_password, user.password):
        raise ValueError("Current password is incorrect")
    user.password = hash_password(req.new_password)
    db.commit()
    logout(user_id, db)


def _handle_oauth(provider: str, social_id: str, email: str, name: str, db: Session) -> dict:
    existing = db.query(SocialAccount).filter(
        SocialAccount.provider == provider, SocialAccount.provider_id == social_id
    ).first()

    if existing:
        user = db.query(User).filter(User.id == existing.user_id, User.deleted_at.is_(None)).first()
    else:
        user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
        if not user:
            user = User(
                name=name, email=email,
                username=email.split("@")[0] + "_" + str(uuid4())[:6],
                password=hash_password(str(uuid4())),
                is_root=False, is_active=True, email_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        sa = SocialAccount(user_id=user.id, provider=provider, provider_id=social_id)
        db.add(sa)
        db.commit()

    return _token_pair(user, db)


def oauth_google(req: OAuthRequest, db: Session) -> dict:
    with httpx.Client() as client:
        r = client.get(f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={req.access_token}")
        r.raise_for_status()
        data = r.json()
    return _handle_oauth("google", data["id"], data["email"], data["name"], db)


def oauth_facebook(req: OAuthRequest, db: Session) -> dict:
    with httpx.Client() as client:
        r = client.get(f"https://graph.facebook.com/me?fields=id,name,email&access_token={req.access_token}")
        r.raise_for_status()
        data = r.json()
    return _handle_oauth("facebook", data["id"], data["email"], data["name"], db)
