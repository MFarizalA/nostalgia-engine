# 🐕 Architecture — Such Nostalgia. Very AI. Wow.

> *Much diagram. Very technical. Such architecture. Wow.*

This document covers the full technical architecture of the Doge Nostalgia Engine — component responsibilities, data flow, sequence diagrams, async job lifecycle, infrastructure layout, and design decisions.

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Component Breakdown](#2-component-breakdown)
3. [High-Level Flow Diagram](#3-high-level-flow-diagram)
4. [Detailed Sequence Diagram](#4-detailed-sequence-diagram)
5. [Async Job Lifecycle](#5-async-job-lifecycle)
6. [Infrastructure Layout](#6-infrastructure-layout)
7. [Data Flow — Step by Step](#7-data-flow--step-by-step)
8. [Design Decisions](#8-design-decisions)
9. [Security Considerations](#9-security-considerations)

---

## 1. Architectural Overview

The Doge Nostalgia Engine follows a **Decoupled Agentic Architecture**. The core design principle is simple: keep the SAS instance lightweight (it only orchestrates) and offload all heavy AI inference to Alibaba Cloud Model Studio's serverless GPU fleet.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ALIBABA CLOUD                            │
│                                                                 │
│  ┌──────────────────────┐       ┌───────────────────────────┐  │
│  │  Simple Application  │       │      Model Studio         │  │
│  │  Server (SAS)        │──────►│  • Qwen3.5             │  │
│  │                      │       │  • Wan2.6-i2v-Flash       │  │
│  │  • Vue.js 3 UI       │◄──────│                           │  │
│  │  • FastAPI Backend   │       └───────────────────────────┘  │
│  │  • Job Store         │                                       │
│  └──────────┬───────────┘       ┌───────────────────────────┐  │
│             │                   │  Object Storage (OSS)     │  │
│             └──────────────────►│  • Generated .mp4 files   │  │
│                                 │  • Signed public URLs     │  │
│                                 └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ▲                  ▲
         │ HTTP             │ Signed URL
         ▼                  ▼
    ┌─────────┐
    │  User   │  (browser / mobile)
    └─────────┘
```

**Key principle:** SAS never touches GPU workloads. It submits jobs, polls status, and coordinates storage. All inference runs serverlessly on Model Studio.

---

## 2. Component Breakdown

### 2.1 Frontend — Vue.js 3 on SAS

| Responsibility | Detail |
|---|---|
| Photo upload UI | Drag-and-drop or file picker; base64-encodes image client-side |
| **Era Selector** | Pill row — 2010 / 2012 / 2014 / 2016 / 2018 / 2020; default 2016 |
| **Festivity Selector** | 4-tile greeting-card grid — None / CNY 🧧 / Ramadan 🌙 / Eid 🎊 |
| **Style Picker** | 5-tile grid — Auto / VSCO / Grunge / Meme-Heavy / Cinemagraph |
| Job submission | `POST /api/generate` with image + era + festivity + style |
| Status polling | `GET /api/status/{job_id}` every 4 seconds via `StatusPoller` |
| Result display | Renders signed `.mp4`, Vibe Score, scene description, **Wan style_prompt** |
| Festivity badge | Shows greeting (e.g. "🌙 Ramadan Kareem") on the result page |

### 2.2 Backend — Python 3.11 / FastAPI on SAS

| Responsibility | Detail |
|---|---|
| Image ingestion | Receives base64 image, validates MIME type and size |
| Dynamic prompt building | Assembles Qwen system prompt from era context + festivity addon + style addon |
| Qwen orchestration | Calls Qwen3.5 with image + dynamic system prompt |
| Prompt extraction | Parses Qwen JSON: `scene_description`, `style_prompt`, `vibe_score` |
| Wan job submission | Calls Wan2.6-i2v-Flash API asynchronously; receives `task_id` |
| Job state tracking | In-memory job store (dict); maps `job_id → status + metadata + style_prompt` |
| Status polling endpoint | Proxies Wan status queries; updates job store on completion |
| OSS upload | On Wan success: streams video bytes to OSS bucket |
| Signed URL generation | Issues time-limited OSS signed URLs; returns to frontend |

### 2.3 Qwen3.5 — Alibaba Cloud Model Studio

| Responsibility | Detail |
|---|---|
| Vision understanding | Interprets subjects, setting, mood, lighting from the uploaded photo |
| Era remixing | Rewrites the scene through the cultural lens of the selected year |
| Festivity overlay | Weaves festive theme (CNY / Ramadan / Eid) into the scene description |
| Style direction | Applies aesthetic mode constraints (VSCO / Grunge / Meme / Cinemagraph) |
| Prompt generation | Outputs a `style_prompt` for Wan to consume |
| Vibe scoring | Returns `vibe_score` (0–100) rating how naturally the photo maps to the chosen era |

**Dynamic system prompt structure:**
```
[BASE PROMPT]
  You are a creative director specialising in internet culture and visual nostalgia.
  Analyse the provided photo and reinterpret it as if captured in {era}.

[ERA CONTEXT — injected per selection]
  2016: "VSCO cams (A4/HB2/C1), Doge meme, Harambe, Pokemon Go, dabbing..."
  2020: "Lo-fi aesthetic, quarantine soft lighting, TikTok grain filter, cottagecore..."
  (6 eras total)

[FESTIVITY ADDON — optional, injected when selected]
  "cny":    "Festive theme — Chinese Lunar New Year: hongbao textures, firecracker bokeh..."
  "ramadan":"Festive theme — Ramadan: fanous lantern bokeh, crescent moon silhouettes..."
  "eid":    "Festive theme — Eid: arabesque gold patterns, fireworks bokeh..."

[STYLE ADDON — optional, injected when selected]
  "vsco":   "Aesthetic mode — VSCO: warm fade (A4), film grain (HB2), golden-hour light..."
  "grunge": "Aesthetic mode — Tumblr Grunge: low contrast, desaturated, gritty dark..."
  "meme":   "Aesthetic mode — Meme-Heavy: Comic Sans, Impact text, reaction faces..."
  "cine":   "Aesthetic mode — Cinemagraph: film grain, anamorphic flare, letterbox..."

[OUTPUT FORMAT]
  Return ONLY valid JSON:
  {
    "scene_description": "<what you see, reframed in {era}>",
    "style_prompt":      "<detailed generative prompt for Wan, 2–3 sentences>",
    "vibe_score":        <integer 0-100>
  }
```

### 2.4 Wan2.6-i2v-Flash — Alibaba Cloud Model Studio

| Responsibility | Detail |
|---|---|
| Image-to-video generation | Conditions on the user's original photo as the anchor frame |
| Style application | Uses Qwen's `style_prompt` to drive the nostalgic transformation |
| Async delivery | Returns `task_id` immediately on `202 Accepted`; video ready in ~30–90 seconds |
| Output format | Short `.mp4` clip (5 seconds) |

### 2.5 Object Storage Service (OSS)

| Responsibility | Detail |
|---|---|
| Video storage | Receives `.mp4` from backend on generation success |
| Access control | Bucket ACL is `private`; no direct public access |
| Signed URL delivery | Backend generates time-limited signed URLs (default: 1 hour TTL) |
| Lifecycle management | Auto-deletes objects after 7 days (configured via OpenTofu) |
| CORS | Allows GET/PUT from the SAS-hosted frontend origin |

---

## 3. High-Level Flow Diagram

```
                         ┌──────────┐
                         │   User   │
                         └────┬─────┘
         Upload + era/         │           Display
         festivity/style       ▼
                      ┌────────────────┐
                      │  Vue.js 3      │◄──────────────────────────┐
                      │  on SAS        │                           │
                      └───────┬────────┘                           │
                              │ POST /api/generate                  │ Signed URL
                              ▼                                     │
          ┌──────────────────────────────────────────────────────────────────┐
          │                  FastAPI Backend on SAS                          │
          │                                                                  │
          │   Builds dynamic Qwen prompt                                     │
          │   (era context + festivity addon + style addon)                  │
          │                │                                                 │
          │                ▼                                                 │
          │   ┌──────────────────────────┐                                   │
          │   │       Qwen3.5            │                                   │
          │   └────────────┬─────────────┘                                   │
          │                │  style_prompt + vibe_score + scene_description  │
          │                ▼                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │   Wan2.6-i2v-Flash       │                                   │
          │   └────────────┬─────────────┘                                   │
          │                │  Generated nostalgic video (.mp4)                │
          │                ▼                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │  Object Storage (OSS)    │───────────────────────────────────┘
          │   └──────────────────────────┘
          └──────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Sequence Diagram

```
User              SAS (FastAPI)            Qwen3.5            Wan             OSS
 │                     │                    │                  │               │
 │── Upload Photo ────►│                    │                  │               │
 │   + era/festivity/  │                    │                  │               │
 │     style params    │                    │                  │               │
 │                     │── Dynamic prompt ──►│                  │               │
 │                     │   (era context +   │                  │               │
 │                     │   festivity addon  │                  │               │
 │                     │   + style addon)   │                  │               │
 │                     │                    │                  │               │
 │                     │◄── JSON response ──│                  │               │
 │                     │    scene_desc      │                  │               │
 │                     │    style_prompt    │                  │               │
 │                     │    vibe_score      │                  │               │
 │                     │                    │                  │               │
 │                     │── i2v request ─────────────────────►  │               │
 │                     │   (style_prompt +  │                  │               │
 │                     │    user photo)     │                  │               │
 │                     │                    │                  │               │
 │                     │◄── 202 Accepted ───────────────────── │               │
 │                     │    task_id         │                  │               │
 │                     │                    │                  │               │
 │◄── 202 + job_id ────│                    │                  │               │
 │    + vibe_score      │                    │                  │               │
 │    + scene_desc      │                    │                  │               │
 │                     │                    │                  │               │
 │   ╔══════════════════════════════════════════════════╗       │               │
 │   ║  POLL LOOP — every 4 seconds                     ║       │               │
 │──►║── GET /api/status/{job_id} ─────────────────────►║       │               │
 │   ║               ── Query Wan status ────────────────────►  │               │
 │   ║               ◄─ "processing..." ─────────────────────── │               │
 │◄──║── { status: "processing" } ──────────────────────║       │               │
 │   ╚══════════════════════════════════════════════════╝       │               │
 │                     │               ◄─ Status: SUCCEEDED ─── │               │
 │                     │── Store .mp4 ──────────────────────────────────────►  │
 │                     │◄── Signed URL ─────────────────────────────────────── │
 │── GET /api/status ─►│                    │                  │               │
 │◄── 200 success ─────│                    │                  │               │
 │    signed_url        │                    │                  │               │
 │    vibe_score        │                    │                  │               │
 │    style_prompt      │                    │                  │               │
 │                     │                    │                  │               │
 │  Display video 🐕   │                    │                  │               │
 │  + festivity badge  │                    │                  │               │
 │  + Wan's direction  │                    │                  │               │
```

---

## 5. Async Job Lifecycle

Wan2.6-i2v-Flash generation takes 30–90 seconds. The backend handles this with a non-blocking async pattern:

```
POST /api/generate
  │
  ├─► [1] Validate & decode image
  ├─► [2] Build dynamic Qwen system prompt (era + festivity + style)
  ├─► [3] Call Qwen3.5 (sync, ~2–4s) → scene_description, style_prompt, vibe_score
  ├─► [4] Upload source image to OSS → signed URL for Wan
  ├─► [5] Submit Wan i2v job → receive task_id (202)
  ├─► [6] Store job in memory: { job_id: { status, vibe_score, scene_desc, style_prompt } }
  └─► [7] Return 202 to frontend immediately

GET /api/status/{job_id}   ← frontend polls every 4s
  │
  ├─► [A] Look up job in memory store
  ├─► [B] If "processing": query Wan API → update memory store
  ├─► [C] If Wan returns "SUCCEEDED":
  │         ├─► Download video bytes from Wan temporary URL
  │         ├─► Upload to OSS
  │         ├─► Generate signed URL (1hr TTL)
  │         ├─► Update job: { status: "success", video_url }
  │         └─► Return 200 with video_url + vibe_score + style_prompt
  └─► [D] If Wan returns "FAILED":
            └─► Update job: { status: "failed", error }
```

### Job State Machine

```
                  ┌──────────┐
   POST /generate │ PENDING  │
  ────────────────►          │
                  └────┬─────┘
                       │ Wan accepted (task_id)
                       ▼
                  ┌────────────┐
                  │ PROCESSING │◄─── poll loop (4s)
                  └──┬──────┬──┘
                     │      │
              success│      │failed
                     ▼      ▼
                ┌───────┐ ┌────────┐
                │SUCCESS│ │ FAILED │
                └───────┘ └────────┘
                     │
                     │ video stored to OSS
                     ▼
              signed URL + style_prompt returned
```

| State | HTTP | Frontend Message |
|---|---|---|
| `pending` | 202 | "Much generate… please wait" |
| `processing` | 200 | "Very rewind… still cooking" |
| `success` | 200 | "Wow. Such {era}. Many nostalgia." 🐕 |
| `failed` | 200 | "Such fail. Very sad. Much retry." |

---

## 6. Infrastructure Layout

All cloud resources are declared in `infra/` using OpenTofu. See [`../infra/`](../infra/) for the full IaC source.

```
Alibaba Cloud (cn-hangzhou)
│
├── Simple Application Server (SAS)
│   ├── Instance: doge-nostalgia-engine
│   │   ├── OS: Ubuntu 22.04 LTS
│   │   ├── Spec: 2 vCPU / 4 GB RAM / 40 GB SSD
│   │   └── Bootstrap: cloud-init → Docker → docker compose up
│   └── Firewall Rules
│       ├── TCP 22   — SSH
│       ├── TCP 80   — Frontend (Vue.js 3)
│       └── TCP 8000 — Backend API (FastAPI)
│
├── Object Storage Service (OSS)
│   ├── Bucket: doge-nostalgia-outputs-[suffix]
│   ├── ACL: private
│   ├── CORS: GET/PUT allowed from SAS origin
│   └── Lifecycle: expire all objects after 7 days
│
└── Model Studio (serverless — no provisioning required)
    ├── Qwen3.5  (qwen-vl-max endpoint)
    └── Wan2.6-i2v-Flash (wan2.6-i2v-flash endpoint)
```

### OpenTofu Module Graph

```
root
 ├── module.oss    → alicloud_oss_bucket
 │                   alicloud_oss_bucket_cors
 │                   alicloud_oss_bucket_lifecycle_rule
 │
 └── module.sas    → alicloud_simple_application_server_instance
   (depends_on oss)  alicloud_simple_application_server_firewall_rule ×3
```

---

## 7. Data Flow — Step by Step

| Step | Actor | Action | Output |
|---|---|---|---|
| 1 | User | Uploads JPEG/PNG + picks era, festivity, style | Selections sent to frontend |
| 2 | Frontend | `POST /api/generate` with `{ image_base64, filename, era, festivity, style }` | HTTP request to SAS |
| 3 | FastAPI | Validates image; decodes base64 | Raw image bytes |
| 4 | FastAPI | Builds dynamic Qwen system prompt (era context + festivity addon + style addon) | Prompt string |
| 5 | FastAPI → Qwen3.5 | Sends image + dynamic system prompt | JSON: `scene_description`, `style_prompt`, `vibe_score` |
| 6 | FastAPI → OSS | Uploads source image | Signed URL for Wan |
| 7 | FastAPI → Wan | Submits i2v job with `style_prompt` + image URL | `task_id`, `202 Accepted` |
| 8 | FastAPI | Stores job state (incl. `style_prompt`) in memory; returns `job_id` + `vibe_score` | `202` response |
| 9 | Frontend | Polls `GET /api/status/{job_id}` every 4 seconds | Status updates |
| 10 | FastAPI → Wan | Queries Wan task status on each poll | `PENDING` / `RUNNING` / `SUCCEEDED` |
| 11 | FastAPI → OSS | On success: uploads `.mp4` to OSS bucket | Object stored |
| 12 | FastAPI → OSS | Generates signed URL (1hr TTL) | `https://...?Expires=...` |
| 13 | FastAPI → Frontend | Returns `{ status: "success", video_url, vibe_score, style_prompt }` | Final `200` response |
| 14 | Frontend | Renders `<video>` + Vibe Score + scene description + Wan's direction | User sees nostalgic video 🐕 |

---

## 8. Design Decisions

### Why a dynamic Qwen prompt instead of a fixed one?

The original system prompt was hardcoded to 2016. By splitting it into a base template + ERA_CONTEXTS (6 eras) + FESTIVITY_ADDONS (3 themes) + STYLE_ADDONS (4 modes), the same pipeline can produce dramatically different outputs without changing any model or infrastructure. The permutation space is 6 × 4 × 5 = 120 distinct aesthetic combinations from a single model call.

### Why store `style_prompt` in the job record and return it to the frontend?

Surfacing the AI's intermediate output (what Qwen told Wan to do) makes the AI pipeline transparent and impressive to judges and users. It also aids debugging — you can see exactly what prompt produced a given video.

### Why decoupled async instead of synchronous?

Wan2.6-i2v-Flash generation takes 30–90 seconds. A synchronous HTTP request would timeout on most clients and proxies. The async `task_id + poll` pattern keeps the frontend responsive and gives the user a live progress experience while the GPU does its work.

### Why FastAPI and not Node.js?

Both are valid. FastAPI was chosen for its native `async/await` support, automatic OpenAPI docs at `/docs`, and Pydantic validation — which reduces boilerplate when handling image payloads and Qwen JSON responses.

### Why OSS signed URLs instead of public bucket access?

Public buckets expose all objects indefinitely. Signed URLs expire (default 1 hour), can be scoped per object, and require no bucket ACL changes. Combined with the 7-day lifecycle rule, this keeps storage minimal and access controlled.

### Why keep job state in memory instead of a database?

For a hackathon demo with a single SAS instance and short-lived jobs, an in-memory dict is sufficient. For production scale, replace with Redis or Alibaba Cloud Table Store for persistence across restarts and horizontal scaling.

### Why SAS instead of ECS + separate load balancer?

SAS bundles compute, networking, firewall, and a managed IP into a single low-config resource. For a single-instance hackathon deployment this is dramatically simpler.

---

## 9. Security Considerations

| Concern | Mitigation |
|---|---|
| API key exposure | `DASHSCOPE_API_KEY` in `.env`, excluded from git via `.gitignore` |
| OSS direct access | Bucket ACL is `private`; all access via backend-generated signed URLs |
| Signed URL TTL | Default 3600s (1 hour); configurable via `OSS_SIGNED_URL_EXPIRY` |
| Image upload abuse | Backend validates MIME type and file size before passing to Qwen |
| Input validation | `era`, `festivity`, `style` values are only applied if present in their respective dicts — unknown values fall back to defaults |
| SSH hardening | Restrict port 22 source CIDR to your IP in `modules/sas/main.tf` for production |
| State file secrets | `terraform.tfvars` and `*.tfstate` excluded from git via `infra/.gitignore` |
| Video retention | OSS lifecycle rule deletes all objects after 7 days |

---

*Such architecture. Very diagram. Wow. 🐕*
*Doge Nostalgia Engine — Alibaba Cloud AI × Creativity Hackathon 2026*
