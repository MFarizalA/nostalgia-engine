"""
Wan2.6-i2v-Flash integration via Alibaba Cloud Model Studio.

Uses the DashScope async video-synthesis REST API directly.
The job is submitted with X-DashScope-Async: enable, returns a task_id
immediately (202 Accepted), and we poll the task endpoint until done.
"""

import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

_VIDEO_SYNTHESIS_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc"
    "/video-generation/video-synthesis"
)
_TASK_STATUS_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

# Wan task status values returned by the API
_TERMINAL_SUCCESS = {"SUCCEEDED"}
_TERMINAL_FAILURE = {"FAILED", "CANCELED", "UNKNOWN"}


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {settings.dashscope_api_key}"}


async def submit_i2v_job(image_url: str, style_prompt: str) -> str:
    """
    Submit an image-to-video job to Wan2.6-i2v-Flash.

    Args:
        image_url:    Publicly accessible URL of the source image
                      (OSS signed URL is fine).
        style_prompt: 2016-era prompt from Qwen.

    Returns:
        Wan task_id string.
    """
    headers = {
        **_auth_headers(),
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    payload = {
        "model": settings.wan_model,
        "input": {
            "prompt":  style_prompt,
            "img_url": image_url,
        },
        "parameters": {
            "duration": 5,          # 5-second clip
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(_VIDEO_SYNTHESIS_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    task_id: str = data["output"]["task_id"]
    logger.info("Wan job submitted — task_id=%s", task_id)
    return task_id


async def get_task_status(task_id: str) -> dict:
    """
    Query the Wan task status endpoint.

    Returns:
        {
            "status":    "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | ...,
            "video_url": str | None   (only present on SUCCEEDED)
        }
    """
    url = _TASK_STATUS_URL.format(task_id=task_id)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=_auth_headers())
        resp.raise_for_status()
        data = resp.json()

    output = data.get("output", {})
    return {
        "status":    output.get("task_status", "UNKNOWN"),
        "video_url": output.get("video_url"),
    }


def is_terminal_success(status: str) -> bool:
    return status in _TERMINAL_SUCCESS


def is_terminal_failure(status: str) -> bool:
    return status in _TERMINAL_FAILURE


async def download_video(video_url: str) -> bytes:
    """Download the generated video from Wan's temporary URL."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.get(video_url)
        resp.raise_for_status()
        return resp.content
