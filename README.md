# 🐕 Such Nostalgia. Very AI. Wow.
### *A Doge-Approved Time Machine — Powered by Alibaba Cloud AI*

> *Much upload. Very rewind. Such video. Wow.*

An AI-powered creative web app that transforms your modern photos into short nostalgic videos styled in the aesthetic of any internet era from 2010 to 2020. Pick a year, choose a festive greeting card theme, dial in an aesthetic mode — and let Qwen3.5 + Wan2.6-i2v-Flash do the rest.

Powered by **Qwen3.5** and **Wan2.6-i2v-Flash** on Alibaba Cloud Model Studio, hosted on a Simple Application Server (SAS).

Built for the **Alibaba Cloud AI × Creativity Hackathon 2026**.

---

## 🐕 What It Does

1. **Such Upload** — drop any photo from your life in 2026
2. **Very Pick** — choose your era (2010–2020), festive theme (CNY / Ramadan / Eid), and aesthetic style (VSCO / Grunge / Meme / Cinemagraph)
3. **Much Analyze** — Qwen3.5 reads the photo and writes an era-appropriate scene description, vibe score, and Wan video direction prompt
4. **Wow Generate** — Wan2.6-i2v-Flash animates your photo with the chosen aesthetic
5. **Such Result** — you receive a short `.mp4` + a **Vibe Score** (0–100) + the AI's full style prompt

---

## 🖥️ Demo

> Live demo URL: `https://your-sas-ip-or-domain`

![App Screenshot](docs/screenshot.png)

---

## ✨ Feature Highlights

### 📅 Era Selector
Choose which internet year to rewind to:

| Era | Cultural Context |
|---|---|
| 2010 | Hipstamatic filters, early Instagram, flip-phone selfies, early Tumblr |
| 2012 | Earlybird/Hefe/X-Pro II, YOLO, Gangnam Style, Vine launch |
| 2014 | #nofilter, selfie sticks, Ice Bucket Challenge, early VSCO |
| **2016** ★ | VSCO cams, Doge meme, Harambe, Pokemon Go, dabbing *(default)* |
| 2018 | Avocado toast, VSCO girl, Drake memes, Instagram Stories |
| 2020 | Lo-fi aesthetic, quarantine lighting, TikTok grain, cottagecore |

### 🎊 Festivity Selector (Greeting Card Mode)
Overlay a festive theme on top of the era aesthetic:

| Theme | Vibe |
|---|---|
| ✨ No theme | Pure internet nostalgia |
| 🧧 Lunar New Year | Hongbao textures, firecracker bokeh, crimson-gold palette |
| 🌙 Ramadan | Fanous lanterns, crescent moon overlays, amber-gold light |
| 🎊 Eid | Arabesque patterns, fireworks bokeh, joyful golden glow |

### 🎞️ Style Picker
Control the aesthetic mode that shapes the video generation:

| Style | Description |
|---|---|
| Auto | Let Qwen3.5 decide based on the photo |
| VSCO | Warm fade, film grain, golden-hour light, #vscocam |
| Grunge | Low contrast, desaturated, dark moody texture |
| Meme-Heavy | Comic Sans overlays, reaction faces, maximum chaos |
| Cinemagraph | Film grain, anamorphic flare, letterbox feel |

### 🤖 AI Transparency
The result page shows:
- **Qwen's 2016 Reframe** — the scene description the AI wrote
- **Wan's Direction** — the exact video generation prompt Qwen produced

---

## 🗂️ Project Structure

```
nostalgia-engine/
├── frontend/                  # Vue.js 3 single-page app
│   ├── src/
│   │   ├── components/        # UploadZone, StatusPoller, VideoResult
│   │   ├── views/             # Landing, Processing, Result
│   │   └── App.vue
│   └── Dockerfile
│
├── backend/                   # Python 3.11 + FastAPI
│   ├── main.py                # API routes
│   ├── models.py              # Pydantic request/response models
│   ├── job_store.py           # In-memory job store
│   ├── services/
│   │   ├── qwen.py            # Qwen3.5 dynamic prompt builder
│   │   ├── wan.py             # Wan2.6-i2v-Flash async job handling
│   │   └── oss.py             # OSS upload + signed URL generation
│   ├── requirements.txt
│   └── Dockerfile
│
├── infra/                     # OpenTofu infrastructure-as-code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── sas/               # Simple Application Server instance + firewall
│       └── oss/               # Object Storage bucket + CORS + lifecycle
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── screenshot.png
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧠 Architecture

```
User → Vue.js (SAS)
     → FastAPI Backend (SAS)
     → Qwen3.5            — analyzes photo + era/festivity/style → scene_description, style_prompt, vibe_score
     → Wan2.6-i2v-Flash   — generates nostalgic video (async, polled every 4s)
     → OSS                — stores .mp4, returns signed URL
     → User sees video + Vibe Score + AI prompt
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full sequence diagram and component breakdown.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Alibaba Cloud account with:
  - **Simple Application Server (SAS)** instance (Ubuntu 22.04, 2 vCPU / 4 GB RAM recommended)
  - **Model Studio** API key (access to `qwen-vl-max` and `wan2.6-i2v-flash`)
  - **OSS** bucket created

---

### 1. Clone the repository

```bash
git clone https://github.com/your-org/nostalgia-engine.git
cd nostalgia-engine
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Alibaba Cloud Model Studio
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Models
QWEN_MODEL=qwen-vl-max
WAN_MODEL=wan2.6-i2v-flash

# OSS
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=nostalgia-engine-outputs
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_SIGNED_URL_EXPIRY=3600
```

### 3. Build and run

```bash
docker compose up -d --build
```

| Service | Port |
|---|---|
| Frontend | `http://localhost:80` |
| Backend API | `http://localhost:8000` |
| API Docs (Swagger) | `http://localhost:8000/docs` |

---

## 🔌 API Endpoints

### `POST /api/generate`

Submit a photo for transformation.

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "<base64>",
    "filename": "photo.jpg",
    "era": 2016,
    "festivity": "eid",
    "style": "vsco"
  }'
```

| Field | Type | Required | Values |
|---|---|---|---|
| `image_base64` | string | ✅ | Base64-encoded JPEG/PNG/WebP |
| `filename` | string | ✅ | Original filename |
| `era` | integer | — | `2010` `2012` `2014` `2016` `2018` `2020` (default: `2016`) |
| `festivity` | string | — | `"cny"` `"ramadan"` `"eid"` (default: `null`) |
| `style` | string | — | `"vsco"` `"grunge"` `"meme"` `"cine"` (default: `null`) |

**Response `202 Accepted`:**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "vibe_score": 78,
  "scene_description": "A casual outdoor moment remixed into 2016 VSCO aesthetic..."
}
```

---

### `GET /api/status/{job_id}`

Poll for job completion.

```bash
curl http://localhost:8000/api/status/abc123
```

**Response on success:**
```json
{
  "job_id": "abc123",
  "status": "success",
  "video_url": "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/video/abc123.mp4?Expires=...",
  "vibe_score": 78,
  "scene_description": "A casual outdoor moment...",
  "style_prompt": "Slow warm zoom with golden bokeh drift, VSCO A4 fade..."
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue.js 3 |
| Backend | Python 3.11 + FastAPI |
| Vision + Prompt AI | Qwen3.5 (Alibaba Cloud Model Studio) |
| Video Generation | Wan2.6-i2v-Flash (Alibaba Cloud Model Studio) |
| Storage | Alibaba Cloud OSS |
| Hosting | Alibaba Cloud SAS (Docker) |
| Infrastructure as Code | OpenTofu ≥ 1.6 + alicloud provider ~> 1.220 |
| Dev Tooling | Qoder AI |

---

## ⚙️ Configuration Reference

| Variable | Description | Default |
|---|---|---|
| `DASHSCOPE_API_KEY` | Model Studio API key | — |
| `QWEN_MODEL` | Qwen model ID | `qwen-vl-max` |
| `WAN_MODEL` | Wan model ID | `wan2.6-i2v-flash` |
| `OSS_BUCKET_NAME` | OSS bucket for video output | — |
| `OSS_ENDPOINT` | OSS regional endpoint | `oss-cn-hangzhou.aliyuncs.com` |
| `OSS_SIGNED_URL_EXPIRY` | Signed URL validity in seconds | `3600` |

---

## 🧪 Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev        # Vite dev server on :5173
```

---

## 📦 Deploying Infrastructure with OpenTofu

All cloud resources are declared in `infra/` and provisioned with [OpenTofu](https://opentofu.org/).

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# fill in access keys, bucket name, SSH key pair
tofu init
tofu plan
tofu apply
```

OpenTofu provisions:
- **OSS bucket** — private, CORS enabled, 7-day video expiry lifecycle
- **SAS instance** — Ubuntu 22.04, Docker pre-installed, app auto-started via cloud-init
- **Firewall rules** — ports 22, 80, 8000

---

## 🪪 License

MIT — see [`LICENSE`](LICENSE) for details.

---

## 🙌 Acknowledgements

- [Alibaba Cloud Model Studio](https://www.alibabacloud.com/product/modelstudio) — Qwen3.5 & Wan2.6-i2v-Flash
- [Alibaba Cloud OSS](https://www.alibabacloud.com/product/oss)
- [Alibaba Cloud SAS](https://www.alibabacloud.com/product/swas)
- Built with [Qoder AI](https://qoder.ai) agentic coding tools

---

*Alibaba Cloud AI × Creativity Hackathon 2026 — Such Nostalgia. Very AI. Wow. 🐕*
