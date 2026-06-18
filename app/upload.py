import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from .config import settings

MAX_SIZE = 2 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
EXT_MAP = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_photo(file: UploadFile) -> str:
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 2MB limit")
    ct = file.content_type or ""
    if ct not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    ext = EXT_MAP.get(ct, ".jpg")
    filename = f"{uuid4()}{ext}"
    os.makedirs(settings.storage_path, exist_ok=True)
    path = os.path.join(settings.storage_path, filename)
    with open(path, "wb") as f:
        f.write(content)
    return filename


def delete_photo(filename: str | None) -> None:
    if not filename:
        return
    path = os.path.join(settings.storage_path, filename)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Failed to delete photo {filename}: {e}")


def build_photo_url(filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{settings.app_url}/storage/photos/{filename}"
