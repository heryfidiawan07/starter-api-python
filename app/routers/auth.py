from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from .. import response as R
from ..deps import get_current_user, get_db
from ..schemas.auth import (
    ChangePasswordRequest, ForgotPasswordRequest, LoginRequest,
    OAuthRequest, RefreshTokenRequest, RegisterRequest,
    ResetPasswordRequest, RevokeTokenRequest,
)
from ..serializers import serialize_user
from ..services import auth_service as svc

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = svc.register(req, db)
    return R.created("Registration successful", serialize_user(user))


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = svc.login(req, db)
    result["user"] = serialize_user(result["user"])
    return R.ok("Login successful", result)


@router.post("/logout")
def logout(current: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    svc.logout(current["user_id"], db)
    return R.ok("Logged out successfully")


@router.post("/refresh")
def refresh(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    result = svc.refresh(req, db)
    return R.ok("Token refreshed", result)


@router.post("/revoke")
def revoke(req: RevokeTokenRequest, current: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    svc.revoke_token(current["user_id"], req, db)
    return R.ok("Token revoked")


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    svc.forgot_password(req, db)
    return R.ok("If the email exists, a reset link has been sent")


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    svc.reset_password(req, db)
    return R.ok("Password reset successful")


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    svc.verify_email(token, db)
    return R.ok("Email verified successfully")


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc.change_password(current["user_id"], req, db)
    return R.ok("Password changed successfully")


@router.post("/oauth/google")
def oauth_google(req: OAuthRequest, db: Session = Depends(get_db)):
    result = svc.oauth_google(req, db)
    result["user"] = serialize_user(result["user"])
    return R.ok("Google OAuth successful", result)


@router.post("/oauth/facebook")
def oauth_facebook(req: OAuthRequest, db: Session = Depends(get_db)):
    result = svc.oauth_facebook(req, db)
    result["user"] = serialize_user(result["user"])
    return R.ok("Facebook OAuth successful", result)
