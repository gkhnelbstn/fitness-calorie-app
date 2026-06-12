"""Öğün fotoğrafı depolama.

Prod (Fly.io diski ephemeral): Supabase Storage'a yükler, public URL döner.
Dev/test (SUPABASE_SERVICE_KEY yok): yerel upload_dir + /uploads/... (mevcut davranış).
"""

from __future__ import annotations

import logging
import mimetypes
import uuid
from pathlib import Path

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


def _supabase_enabled() -> bool:
    s = get_settings()
    return bool(s.supabase_project_url.strip() and s.supabase_service_key.strip())


async def save_photo(content: bytes, suffix: str) -> str:
    """Fotoğrafı kaydet; <img src> olarak kullanılabilir path/URL döndür."""
    fname = f"{uuid.uuid4().hex}{suffix}"
    if _supabase_enabled():
        return await _upload_supabase(content, fname)
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / fname).write_bytes(content)
    return f"/uploads/{fname}"


async def _upload_supabase(content: bytes, fname: str) -> str:
    s = get_settings()
    base = s.supabase_project_url.rstrip("/")
    bucket = s.supabase_storage_bucket
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{base}/storage/v1/object/{bucket}/{fname}",
            headers={
                "Authorization": f"Bearer {s.supabase_service_key}",
                "Content-Type": ctype,
                "x-upsert": "false",
            },
            content=content,
        )
    if resp.status_code not in (200, 201):
        logger.error("Supabase Storage upload başarısız: %s %s", resp.status_code, resp.text[:200])
        raise RuntimeError(f"Foto yüklenemedi (Storage {resp.status_code}).")
    # Public bucket: doğrudan public URL.
    return f"{base}/storage/v1/object/public/{bucket}/{fname}"
