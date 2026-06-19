from fastapi import APIRouter

from .. import response as R
from ..config import settings

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("")
def get_config():
    return R.ok("Config retrieved", {
        "google_client_id": settings.google_client_id,
        "facebook_app_id": settings.facebook_client_id,
    })
