# 🐕 Architecture — Such Nostalgia. Very 2016. Wow.

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
│  │  Server (SAS)        │──────►│  • Qwen3.5-Vision         │  │
│  │                      │       │  • Wan2.6-i2v-Flash       │  │
│  │  • Vue/React UI      │◄──────│                           │  │
│  │  • FastAPI Backend   │       └───────────────────────────┘  │
│  │  • Job Queue         │                                       │
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

### 2.1 Frontend — Vue.js / React on SAS

| Responsibility | Detail |
|---|---|
| Photo upload UI | Drag-and-drop or file picker; base64-encodes image client-side |
| Job submission | `POST /api/generate` with image payload |
| Status polling | `GET /api/status/{job_id}` every 3–5 seconds via `setInterval` |
| Result display | Renders signed `.mp4` URL in a `<video>` element |
| Vibe Score display | Animated score counter (0–100) with Doge commentary |

### 2.2 Backend — Python 3.11 / FastAPI on SAS

| Responsibility | Detail |
|---|---|
| Image ingestion | Receives base64 image, validates type/size |
| Qwen orchestration | Calls Qwen3.5-Vision with image + nostalgia system prompt |
| Prompt extraction | Parses Qwen JSON response: `scene_description`, `style_prompt`, `vibe_score` |
| Wan job submission | Calls Wan2.6-i2v-Flash API asynchronously; receives `JobID` |
| Job state tracking | In-memory job store (dict); maps `job_id → status + metadata` |
| Status polling endpoint | Proxies Wan status queries; updates job store on completion |
| OSS upload | On Wan success: streams video bytes to OSS bucket |
| Signed URL generation | Issues time-limited OSS signed URL; returns to frontend |

### 2.3 Qwen3.5-Vision — Alibaba Cloud Model Studio

| Responsibility | Detail |
|---|---|
| Vision understanding | Interprets subjects, setting, mood, lighting from the uploaded photo |
| Era remixing | Rewrites the scene description through the lens of 2016 aesthetics |
| Prompt generation | Outputs a structured `style_prompt` for Wan to consume |
| Vibe scoring | Returns a `vibe_score` (0–100) rating how naturally the photo maps to 2016 culture |

**System prompt structure:**
```
You are a creative director specializing in 2010s internet culture and visual aesthetics.
Analyze the provided photo and reinterpret it as if captured in 2016.

Style references:
- VSCO cam filters (A4, HB1, HB2)
- Early Instagram square crops
- Shallow depth-of-field selfie aesthetic
- Oversaturated golden-hour tones
- Peak Doge / meme era cultural context

Return ONLY valid JSON:
{
  "scene_description": "<what you see, reframed in 2016>",
  "style_prompt": "<detailed generative prompt for Wan>",
  "vibe_score": <integer 0-100>
}
```

### 2.4 Wan2.6-i2v-Flash — Alibaba Cloud Model Studio

| Responsibility | Detail |
|---|---|
| Image-to-video generation | Conditions on the user's original photo as the anchor frame |
| Style application | Uses Qwen's `style_prompt` to drive the 2016 aesthetic transformation |
| Async delivery | Returns `JobID` immediately on `202 Accepted`; video ready in ~30–90 seconds |
| Output format | Short `.mp4` clip (typically 3–5 seconds) |

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
              Upload           │           Display
            Image/Text         ▼
                      ┌────────────────┐
                      │  Vue / React   │◄──────────────────────────┐
                      │  on SAS        │                           │
                      └───────┬────────┘                           │
                    API       │                                     │
                    Request   ▼                                     │ Signed URL
          ┌──────────────────────────────────────────────────────────────────┐
          │                  Alibaba Cloud Model Studio                      │
          │                                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │  FastAPI Backend on SAS  │                                   │
          │   └────────────┬─────────────┘                                   │
          │                │  Image + Nostalgia Prompt                        │
          │                ▼                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │    Qwen3.5-Vision        │                                   │
          │   └────────────┬─────────────┘                                   │
          │                │  style_prompt + vibe_score                       │
          │                ▼                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │   Wan2.6-i2v-Flash       │                                   │
          │   └────────────┬─────────────┘                                   │
          │                │  Generated 2016 Video (.mp4)                     │
          │                ▼                                                  │
          │   ┌──────────────────────────┐                                   │
          │   │  Object Storage (OSS)    │───────────────────────────────────┘
          │   └──────────────────────────┘
          └──────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Sequence Diagram

```
User              SAS (FastAPI)            Qwen               Wan             OSS
 │                     │                    │                  │               │
 │── Upload Photo ────►│                    │                  │               │
 │   (2026 context)    │                    │                  │               │
 │                     │── Analyze image ──►│                  │               │
 │                     │   + nostalgia      │                  │               │
 │                     │   system prompt    │                  │               │
 │                     │                    │                  │               │
 │                     │◄── JSON response ──│                  │               │
 │                     │    scene_desc      │                  │               │
 │                     │    style_prompt    │                  │               │
 │                     │    vibe_score      │                  │               │
 │                     │                    │                  │               │
 │                     │── i2v request: ────────────────────►  │               │
 │                     │   style_prompt +   │                  │               │
 │                     │   user photo       │                  │               │
 │                     │                    │                  │               │
 │                     │◄── 202 Accepted ───────────────────── │               │
 │                     │    JobID           │                  │               │
 │                     │                    │                  │               │
 │◄── 202 + JobID ─────│                    │                  │               │
 │    + vibe_score      │                    │                  │               │
 │    + "pending"       │                    │                  │               │
 │                     │                    │                  │               │
 │   ╔══════════════════════════════════════════════════╗       │               │
 │   ║  POLL LOOP — every 3–5 seconds                   ║       │               │
 │──►║── GET /api/status/{job_id} ─────────────────────►║       │               │
 │   ║               ── Query Wan status ────────────────────►  │               │
 │   ║               ◄─ "processing..." ─────────────────────── │               │
 │◄──║── { status: "processing" } ────────────────────── ║      │               │
 │   ╚══════════════════════════════════════════════════╝       │               │
 │                     │               ◄─ Status: Success ───── │               │
 │                     │                  (video data)          │               │
 │                     │── Store .mp4 ──────────────────────────────────────►  │
 │                     │◄── Signed URL ─────────────────────────────────────── │
 │── GET /api/status ─►│                    │                  │               │
 │◄── 200 success ─────│                    │                  │               │
 │    signed_url        │                    │                  │               │
 │    vibe_score        │                    │                  │               │
 │                     │                    │                  │               │
 │  Display video! 🐕  │                    │                  │               │
```

---

## 5. Async Job Lifecycle

Wan2.6-i2v-Flash generation takes 30–90 seconds. The backend handles this with a non-blocking async pattern:

```
POST /api/generate
  │
  ├─► [1] Validate & decode image
  ├─► [2] Call Qwen3.5-Vision (sync, ~2–4s)
  ├─► [3] Submit Wan i2v job → receive JobID (202)
  ├─► [4] Store job in memory: { job_id: { status, vibe_score, scene_desc } }
  └─► [5] Return 202 to frontend immediately

GET /api/status/{job_id}   ← frontend polls every 3–5s
  │
  ├─► [A] Look up job in memory store
  ├─► [B] If "processing": query Wan API → update memory store
  ├─► [C] If Wan returns "success":
  │         ├─► Download video bytes from Wan
  │         ├─► Upload to OSS
  │         ├─► Generate signed URL (1hr TTL)
  │         ├─► Update job: { status: "success", video_url, vibe_score }
  │         └─► Return 200 with video_url + vibe_score
  └─► [D] If Wan returns "failed":
            └─► Update job: { status: "failed", error }
```

### Job State Machine

```
                  ┌──────────┐
   POST /generate │  PENDING │
  ────────────────►          │
                  └────┬─────┘
                       │ Wan accepted (JobID)
                       ▼
                  ┌────────────┐
                  │ PROCESSING │◄─── poll loop (3–5s)
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
              signed URL returned
```

| State | HTTP | Frontend Message |
|---|---|---|
| `pending` | 202 | "Much generate… please wait" |
| `processing` | 200 | "Very rewind… still cooking" |
| `success` | 200 | "Wow. Such 2016. Many nostalgia." 🐕 |
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
│       ├── TCP 80   — Frontend (Vue/React)
│       └── TCP 8000 — Backend API (FastAPI)
│
├── Object Storage Service (OSS)
│   ├── Bucket: doge-nostalgia-outputs-[suffix]
│   ├── ACL: private
│   ├── CORS: GET/PUT allowed from SAS origin
│   └── Lifecycle: expire all objects after 7 days
│
└── Model Studio (serverless — no provisioning required)
    ├── Qwen3.5-Vision  (qwen3.5-plus endpoint)
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
| 1 | User | Uploads JPEG/PNG via browser | Base64-encoded image string |
| 2 | Frontend | `POST /api/generate` with `{ image_base64, filename }` | HTTP request to SAS |
| 3 | FastAPI | Validates image; decodes base64 | Raw image bytes |
| 4 | FastAPI → Qwen | Sends image + nostalgia system prompt | JSON: `scene_description`, `style_prompt`, `vibe_score` |
| 5 | FastAPI → Wan | Submits i2v job with `style_prompt` + image | `JobID`, `202 Accepted` |
| 6 | FastAPI | Stores job state in memory; returns `JobID` + `vibe_score` to frontend | `202` response |
| 7 | Frontend | Polls `GET /api/status/{job_id}` every 3–5 seconds | Status updates |
| 8 | FastAPI → Wan | Queries Wan job status on each poll | `processing` or `success` |
| 9 | FastAPI → OSS | On success: uploads `.mp4` to OSS bucket | Object stored |
| 10 | FastAPI → OSS | Generates signed URL (1hr TTL) | `https://...?Expires=...` |
| 11 | FastAPI → Frontend | Returns `{ status: "success", video_url, vibe_score }` | Final `200` response |
| 12 | Frontend | Renders `<video src=video_url>` + Vibe Score | User sees nostalgic video 🐕 |

---

## 8. Design Decisions

### Why decoupled async instead of synchronous?

Wan2.6-i2v-Flash generation takes 30–90 seconds. A synchronous HTTP request would timeout on most clients and proxies. The async `JobID + poll` pattern keeps the frontend responsive and gives the user a live progress experience while the GPU does its work.

### Why FastAPI and not Node.js?

Both are valid. FastAPI was chosen for its native `async/await` support, automatic OpenAPI docs at `/docs`, and Pydantic validation — which reduces boilerplate when handling image payloads and Qwen JSON responses.

### Why OSS signed URLs instead of public bucket access?

Public buckets expose all objects indefinitely. Signed URLs expire (default 1 hour), can be scoped per object, and require no bucket ACL changes. Combined with the 7-day lifecycle rule, this keeps storage minimal and access controlled.

### Why keep job state in memory instead of a database?

For a hackathon demo with a single SAS instance and short-lived jobs, an in-memory dict is sufficient. For production scale, replace with Redis or Alibaba Cloud Table Store for persistence across restarts and horizontal scaling.

### Why SAS instead of ECS + separate load balancer?

SAS bundles compute, networking, firewall, and a managed IP into a single low-config resource. For a single-instance hackathon deployment this is dramatically simpler. The OpenTofu `module.sas` reflects this — it's just 3 firewall rules and one instance resource.

---

## 9. Security Considerations

| Concern | Mitigation |
|---|---|
| API key exposure | `DASHSCOPE_API_KEY` in `.env`, excluded from git via `.gitignore` |
| OSS direct access | Bucket ACL is `private`; all access via backend-generated signed URLs |
| Signed URL TTL | Default 3600s (1 hour); configurable via `OSS_SIGNED_URL_EXPIRY` |
| Image upload abuse | Backend validates MIME type and file size before passing to Qwen |
| SSH hardening | Restrict port 22 source CIDR to your IP in `modules/sas/main.tf` for production |
| State file secrets | `terraform.tfvars` and `*.tfstate` excluded from git via `infra/.gitignore` |
| Video retention | OSS lifecycle rule deletes all objects after 7 days |

---

*Such architecture. Very diagram. Wow. 🐕*
*Doge Nostalgia Engine — Alibaba Cloud AI × Creativity Hackathon 2026*
