"""
Alibaba Cloud OSS — upload and signed URL generation.

oss2 is synchronous, so all public functions run the blocking
calls inside asyncio.to_thread() to avoid blocking the event loop.
"""

import asyncio
import logging
import oss2
from config import settings

logger = logging.getLogger(__name__)


def _bucket() -> oss2.Bucket:
    auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
    return oss2.Bucket(
        auth,
        f"https://{settings.oss_endpoint}",
        settings.oss_bucket_name,
    )


def _sync_upload(object_key: str, data: bytes, content_type: str) -> None:
    _bucket().put_object(
        object_key,
        data,
        headers={"Content-Type": content_type},
    )
    logger.info("OSS upload OK — key=%s (%d bytes)", object_key, len(data))


def _sync_sign_url(object_key: str) -> str:
    url: str = _bucket().sign_url(
        "GET",
        object_key,
        settings.oss_signed_url_expiry,
    )
    return url


async def upload(object_key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
    """Upload bytes to OSS (non-blocking)."""
    await asyncio.to_thread(_sync_upload, object_key, data, content_type)


async def sign_url(object_key: str) -> str:
    """Generate a time-limited signed GET URL (non-blocking)."""
    url = await asyncio.to_thread(_sync_sign_url, object_key)
    logger.info("OSS signed URL issued — key=%s ttl=%ds", object_key, settings.oss_signed_url_expiry)
    return url
