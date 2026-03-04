"""
Qwen3.5-Vision integration via Alibaba Cloud Model Studio.

Uses the OpenAI-compatible endpoint so the standard `openai` SDK
can drive it — no proprietary DashScope SDK required.
"""

import json
import re
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

# ── System prompt (as per ARCHITECTURE.md) ──────────────────────────────────
SYSTEM_PROMPT = """You are a creative director specializing in 2010s internet culture and visual aesthetics.
Analyze the provided photo and reinterpret it as if captured in 2016.

Style references:
- VSCO cam filters (A4, HB1, HB2)
- Early Instagram square crops
- Shallow depth-of-field selfie aesthetic
- Oversaturated golden-hour tones
- Peak Doge / meme era cultural context

Return ONLY valid JSON with no markdown fences, no explanation:
{
  "scene_description": "<what you see, reframed in 2016>",
  "style_prompt": "<detailed generative video prompt for Wan image-to-video>",
  "vibe_score": <integer 0-100>
}"""

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
    return _client


def _parse_response(raw: str) -> dict:
    """Strip optional markdown code fences and parse JSON."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def analyze_photo(image_base64: str, mime_type: str = "image/jpeg") -> dict:
    """
    Call Qwen3.5-Vision with the nostalgia system prompt.

    Returns:
        {
            "scene_description": str,
            "style_prompt":      str,
            "vibe_score":        int (0-100)
        }
    """
    client = _get_client()

    response = await client.chat.completions.create(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Analyze this photo and return ONLY the JSON object "
                            "as described in your instructions."
                        ),
                    },
                ],
            },
        ],
        max_tokens=1024,
    )

    raw = response.choices[0].message.content or ""
    logger.debug("Qwen raw response: %s", raw[:200])

    parsed = _parse_response(raw)

    return {
        "scene_description": str(parsed.get("scene_description", "")),
        "style_prompt":      str(parsed.get("style_prompt", "")),
        "vibe_score":        max(0, min(100, int(parsed.get("vibe_score", 50)))),
    }
