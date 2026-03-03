"""
Doge Nostalgia Engine — FastAPI Backend
Such 2016. Very API. Wow. 🐕

Endpoints:
  POST /api/generate           — submit photo, kick off Qwen + Wan pipeline
  GET  /api/status/{job_id}    — poll job progress / retrieve signed video URL
  GET  /health                 — liveness probe
"""

import base64
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings  # noqa: F401 (validates env on startup)
from models import GenerateRequest, GenerateResponse, StatusResponse
from job_store import JobRecord, put, get, update
from services import qwen, wan, oss

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🐕  Nostalgia Engine starting — such server, very FastAPI, wow")
    yield
    logger.info("🐕  Nostalgia Engine stopping — much graceful shutdown")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Doge Nostalgia Engine",
    description="Such 2016. Very API. Wow. 🐕",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to SAS origin in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Image validation helpers ──────────────────────────────────────────────────

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

_MAGIC: dict[bytes, str] = {
    b"\xff\xd8\xff":             "image/jpeg",
    b"\x89PNG\r\n\x1a\n":       "image/png",
}


def _detect_mime(data: bytes) -> str | None:
    for magic, mime in _MAGIC.items():
        if data[: len(magic)] == magic:
            return mime
    # WebP: "RIFF....WEBP"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def _mime_to_ext(mime: str) -> str:
    return {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime, "bin")


# ── POST /api/generate ────────────────────────────────────────────────────────

@app.post("/api/generate", status_code=202, response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """
    1. Validate & decode image
    2. Call Qwen3.5-Vision  → scene_description, style_prompt, vibe_score
    3. Upload source image to OSS  → signed URL for Wan
    4. Submit Wan2.6-i2v-Flash job  → wan_task_id
    5. Store job in memory, return 202 immediately
    """

    # ── 1. Decode & validate ─────────────────────────────────────────────────
    try:
        image_bytes = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(400, detail="Such corrupt base64. Very unreadable. Wow.")

    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(413, detail="Much big image. Max 10 MB allowed.")

    mime_type = _detect_mime(image_bytes)
    if mime_type is None:
        raise HTTPException(415, detail="Such wrong format. Only JPEG / PNG / WebP.")

    job_id = str(uuid.uuid4())
    ext    = _mime_to_ext(mime_type)
    logger.info("Job %s — image received: %s, %d bytes", job_id, mime_type, len(image_bytes))

    # ── 2. Qwen3.5-Vision (~2–4 s) ──────────────────────────────────────────
    try:
        qwen_result = await qwen.analyze_photo(req.image_base64, mime_type)
    except Exception as exc:
        logger.exception("Job %s — Qwen error", job_id)
        raise HTTPException(502, detail=f"Such Qwen fail. Very error: {exc}")

    scene_description = qwen_result["scene_description"]
    style_prompt      = qwen_result["style_prompt"]
    vibe_score        = qwen_result["vibe_score"]
    logger.info("Job %s — Qwen OK: vibe_score=%d", job_id, vibe_score)

    # ── 3. Upload source image to OSS (Wan needs a URL, not raw bytes) ───────
    source_key = f"source/{job_id}.{ext}"
    try:
        await oss.upload(source_key, image_bytes, mime_type)
        image_url = await oss.sign_url(source_key)
    except Exception as exc:
        logger.exception("Job %s — OSS source upload error", job_id)
        raise HTTPException(502, detail=f"Such OSS fail. Very upload error: {exc}")

    # ── 4. Submit Wan i2v job ────────────────────────────────────────────────
    try:
        wan_task_id = await wan.submit_i2v_job(image_url, style_prompt)
    except Exception as exc:
        logger.exception("Job %s — Wan submit error", job_id)
        raise HTTPException(502, detail=f"Such Wan fail. Very submit error: {exc}")

    logger.info("Job %s — Wan task submitted: %s", job_id, wan_task_id)

    # ── 5. Persist & return 202 ──────────────────────────────────────────────
    put(JobRecord(
        job_id=job_id,
        status="processing",
        wan_task_id=wan_task_id,
        vibe_score=vibe_score,
        scene_description=scene_description,
    ))

    return GenerateResponse(
        job_id=job_id,
        status="processing",
        vibe_score=vibe_score,
        scene_description=scene_description,
    )


# ── GET /api/status/{job_id} ──────────────────────────────────────────────────

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str) -> StatusResponse:
    """
    Poll-friendly status endpoint.

    - Returns cached state if job is already terminal (success / failed).
    - Otherwise queries Wan for the latest task status.
    - On Wan SUCCEEDED: downloads video, uploads to OSS, issues signed URL.
    """
    record = get(job_id)
    if record is None:
        raise HTTPException(404, detail="Such not found. Very missing job_id. Wow.")

    # ── Already terminal — serve from cache ──────────────────────────────────
    if record.status in ("success", "failed"):
        return _to_response(record)

    # ── Query Wan ────────────────────────────────────────────────────────────
    try:
        wan_status = await wan.get_task_status(record.wan_task_id)
    except Exception as exc:
        logger.warning("Job %s — Wan status query failed: %s", job_id, exc)
        # Don't fail the job on a transient network error; frontend will retry
        return StatusResponse(
            job_id=job_id,
            status="processing",
            vibe_score=record.vibe_score,
            scene_description=record.scene_description,
        )

    task_status = wan_status["status"]
    logger.debug("Job %s — Wan task_status=%s", job_id, task_status)

    # ── SUCCEEDED: download → OSS → sign ─────────────────────────────────────
    if wan.is_terminal_success(task_status):
        temp_video_url = wan_status.get("video_url")
        if not temp_video_url:
            _fail(job_id, "Wan SUCCEEDED but returned no video_url")
            return _to_response(get(job_id))

        try:
            video_bytes = await wan.download_video(temp_video_url)
            video_key   = f"video/{job_id}.mp4"
            await oss.upload(video_key, video_bytes, "video/mp4")
            signed_url  = await oss.sign_url(video_key)
        except Exception as exc:
            logger.exception("Job %s — OSS video upload error", job_id)
            _fail(job_id, str(exc))
            return _to_response(get(job_id))

        update(job_id, status="success", video_url=signed_url)
        logger.info("Job %s — complete! Video stored in OSS.", job_id)
        return _to_response(get(job_id))

    # ── FAILED / CANCELED ─────────────────────────────────────────────────────
    if wan.is_terminal_failure(task_status):
        _fail(job_id, f"Wan task status: {task_status}")
        return _to_response(get(job_id))

    # ── Still PENDING / RUNNING ───────────────────────────────────────────────
    return StatusResponse(
        job_id=job_id,
        status="processing",
        vibe_score=record.vibe_score,
        scene_description=record.scene_description,
    )


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Such alive. Very server. Wow. 🐕"}


# ── Private helpers ───────────────────────────────────────────────────────────

def _fail(job_id: str, reason: str) -> None:
    update(job_id, status="failed", error=reason)
    logger.error("Job %s — failed: %s", job_id, reason)


def _to_response(record: JobRecord) -> StatusResponse:
    return StatusResponse(
        job_id=record.job_id,
        status=record.status,
        video_url=record.video_url,
        vibe_score=record.vibe_score,
        scene_description=record.scene_description,
        error=record.error,
    )
