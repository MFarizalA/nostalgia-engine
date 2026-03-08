"""
Qwen3.5 integration via Alibaba Cloud Model Studio.

Uses the OpenAI-compatible endpoint so the standard `openai` SDK
can drive it — no proprietary DashScope SDK required.
"""

import json
import re
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

# ── Era-specific culture contexts ────────────────────────────────────────────
ERA_CONTEXTS: dict[int, str] = {
    2010: (
        "Hipstamatic filters, early square Instagram crops, flip-phone selfie "
        "aesthetic, early Tumblr vibes, lo-fi bedroom pop culture, low-res "
        "point-and-shoot feel, sepia and cross-process looks."
    ),
    2012: (
        "Instagram Earlybird/Hefe/X-Pro II filters, YOLO culture, Call Me Maybe "
        "era, Gangnam Style meme explosion, Keek/Vine launch energy, heavy "
        "vignette, over-saturated summer palettes."
    ),
    2014: (
        "#nofilter irony movement, selfie sticks, Ice Bucket Challenge energy, "
        "early VSCO filters, Throwback Thursday culture, flat lay photography, "
        "minimal white backgrounds, first iPhone slow-mo."
    ),
    2016: (
        "VSCO cams (A4/HB2/C1), Doge meme, Harambe, Pokemon Go, dabbing, "
        "fidget spinner hype, peak Instagram golden-hour selfies, boomerang "
        "loops, live stories, #blessed #aesthetic era."
    ),
    2018: (
        "Avocado toast flat-lay aesthetic, early VSCO girl culture, Drake meme "
        "energy, Instagram Stories format, pastel minimalism, millennial pink, "
        "succulent plants, rose gold everything."
    ),
    2020: (
        "Lo-fi chill-hop aesthetic, quarantine soft natural window lighting, "
        "TikTok grain filter, cottagecore / dark academia, sourdough bread, "
        "cozy indoor plant-filled vibes, muted earth tones."
    ),
}

# ── Festivity overlay prompts ─────────────────────────────────────────────────
FESTIVITY_ADDONS: dict[str, str] = {
    "cny": (
        "Festive theme — Chinese Lunar New Year: weave in red envelope (hongbao) "
        "textures, golden firecracker bokeh bursts, vivid crimson-gold colour "
        "palette, lucky knot motifs, #GongXiFaCai #HappyLunarNewYear overlays. "
        "The style_prompt MUST include: red firecracker sparks drifting across "
        "frame, golden shimmer particle rain, warm festive slow zoom-in."
    ),
    "ramadan": (
        "Festive theme — Ramadan: layer in glowing fanous lantern bokeh, crescent "
        "moon and star silhouettes, warm amber-gold colour palette, mosque "
        "silhouette at dusk, #RamadanKareem #blessed overlays. "
        "The style_prompt MUST include: glowing lantern particles drifting upward, "
        "warm golden light rays from upper frame, serene holy-month atmosphere."
    ),
    "eid": (
        "Festive theme — Eid al-Fitr: incorporate celebratory gold geometric "
        "arabesque patterns, soft fireworks bokeh, ornate border overlays, "
        "#EidMubarak #EidSaid #blessed hashtag text. "
        "The style_prompt MUST include: golden light burst from centre, soft "
        "confetti particles floating, joyful warm glow drift with gentle zoom."
    ),
}

# ── Aesthetic style modifiers ─────────────────────────────────────────────────
STYLE_ADDONS: dict[str, str] = {
    "vsco": (
        "Aesthetic mode — VSCO: prioritise warm fade (A4 filter), film grain "
        "(HB2), natural golden-hour backlight, shallow depth of field with "
        "soft bokeh, muted warm tones, #vscocam #nofilter #aesthetic captions."
    ),
    "grunge": (
        "Aesthetic mode — Tumblr Grunge: low contrast, heavily desaturated, "
        "gritty dark texture, moody deep shadows, crushed blacks, occasional "
        "black-and-white palette with a single vivid colour pop."
    ),
    "meme": (
        "Aesthetic mode — Meme-Heavy: maximum chaotic internet energy, Comic Sans "
        "and Impact font text overlays with white outline, reaction-face "
        "references, bright clashing colours, busy composition, peak 2010s "
        "internet absurdism."
    ),
    "cine": (
        "Aesthetic mode — Cinemagraph: cinematic film grain, anamorphic lens "
        "flare, light leaks on frame edges, subtle slow-motion feel, 2.35:1 "
        "letterbox crop suggestion, cool-warm colour split toning."
    ),
}

# ── Base system prompt (era/festivity/style injected dynamically) ─────────────
_BASE_PROMPT = """You are a creative director specialising in internet culture and visual nostalgia.
Analyse the provided photo and reinterpret it as if captured in {era}.

Era-specific cultural context for {era}:
{era_context}

Visual style references to weave into the style_prompt:
- Early Instagram square crop with heavy vignette
- Shallow depth-of-field selfie aesthetic, lens flare
- Oversaturated golden-hour / sunset tones
- Cinemagraph / GIF era: subtle bokeh, film grain, light leaks
- Snapchat / Vine energy: raw, unfiltered, candid
{extra_addons}
The style_prompt should direct the video animation: describe CAMERA MOVEMENT (slow zoom, gentle pan, handheld shake), LIGHTING (golden hour, lens flare, warm fade), and ATMOSPHERE (nostalgic, dreamy). Vary the style each time — do NOT always use the same elements.

Return ONLY valid JSON with no markdown fences, no explanation:
{{
  "scene_description": "<what you see, reframed in {era} internet culture>",
  "style_prompt": "<rich, varied generative video prompt for Wan image-to-video, 2-3 sentences>",
  "vibe_score": <integer 0-100>
}}"""

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
    return _client


def _build_system_prompt(era: int, festivity: str | None, style: str | None) -> str:
    era_context = ERA_CONTEXTS.get(era, ERA_CONTEXTS[2016])
    extras: list[str] = []
    if festivity and festivity in FESTIVITY_ADDONS:
        extras.append(FESTIVITY_ADDONS[festivity])
    if style and style in STYLE_ADDONS:
        extras.append(STYLE_ADDONS[style])
    extra_block = ("\n" + "\n".join(f"- {e}" for e in extras)) if extras else ""
    return _BASE_PROMPT.format(
        era=era,
        era_context=era_context,
        extra_addons=extra_block,
    )


def _parse_response(raw: str) -> dict:
    """Strip optional markdown code fences and parse JSON."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def analyze_photo(
    image_base64: str,
    mime_type: str = "image/jpeg",
    festivity: str | None = None,
    era: int = 2016,
    style: str | None = None,
) -> dict:
    """
    Call Qwen3.5 with a dynamically built nostalgia system prompt.

    Returns:
        {
            "scene_description": str,
            "style_prompt":      str,
            "vibe_score":        int (0-100)
        }
    """
    client = _get_client()
    system_prompt = _build_system_prompt(era, festivity, style)

    response = await client.chat.completions.create(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": system_prompt},
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
                            "Analyse this photo and return ONLY the JSON object "
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

    try:
        parsed = _parse_response(raw)
    except Exception as exc:
        logger.error("Qwen JSON parse failed: %s — raw: %s", exc, raw[:300])
        raise ValueError(f"Qwen returned invalid JSON: {exc}") from exc

    return {
        "scene_description": str(parsed.get("scene_description", "")),
        "style_prompt":      str(parsed.get("style_prompt", "")),
        "vibe_score":        max(0, min(100, int(parsed.get("vibe_score", 50)))),
    }
