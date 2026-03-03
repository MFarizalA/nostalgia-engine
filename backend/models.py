from pydantic import BaseModel
from typing import Optional


class GenerateRequest(BaseModel):
    image_base64: str
    filename: str


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    vibe_score: Optional[int] = None
    scene_description: Optional[str] = None


class StatusResponse(BaseModel):
    job_id: str
    status: str                        # pending | processing | success | failed
    video_url: Optional[str] = None
    vibe_score: Optional[int] = None
    scene_description: Optional[str] = None
    error: Optional[str] = None
