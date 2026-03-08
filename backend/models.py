from pydantic import BaseModel
from typing import Optional


class GenerateRequest(BaseModel):
    image_base64: str
    filename: str
    festivity: Optional[str] = None   # "cny" | "ramadan" | "eid" | None
    era: Optional[int] = 2016         # 2010 | 2012 | 2014 | 2016 | 2018 | 2020
    style: Optional[str] = None       # "vsco" | "grunge" | "meme" | "cine" | None


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
    style_prompt: Optional[str] = None
    error: Optional[str] = None
