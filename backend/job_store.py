"""
In-memory job store.

For production with multiple replicas, replace with Redis or
Alibaba Cloud Table Store. The interface is intentionally thin
so swapping the backing store only requires changing this file.
"""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class JobRecord:
    job_id:            str
    status:            str               # pending | processing | success | failed
    wan_task_id:       Optional[str]  = None
    vibe_score:        Optional[int]  = None
    scene_description: Optional[str] = None
    video_url:         Optional[str] = None
    error:             Optional[str] = None
    created_at:        float          = field(default_factory=time.time)


# Simple dict — sufficient for a single-instance deployment
_store: dict[str, JobRecord] = {}


def put(record: JobRecord) -> None:
    _store[record.job_id] = record


def get(job_id: str) -> Optional[JobRecord]:
    return _store.get(job_id)


def update(job_id: str, **kwargs) -> Optional[JobRecord]:
    record = _store.get(job_id)
    if record:
        for key, val in kwargs.items():
            setattr(record, key, val)
    return record
