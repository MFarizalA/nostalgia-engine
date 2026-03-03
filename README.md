# 🐕 Such Nostalgia. Very 2016. Wow.
### *A Doge-Approved Time Machine — Powered by Alibaba Cloud AI*

> *Much upload. Very 2016. Such video. Wow.*

An AI-powered creative web app that transforms your modern photos into short videos styled in the aesthetic of 2016 — VSCO filters, early Instagram vibes, and peak Doge-era energy. Powered by **Qwen3.5-Vision** and **Wan2.6-i2v-Flash** on Alibaba Cloud, hosted on a Simple Application Server (SAS).

Built for the **Alibaba Cloud AI × Creativity Hackathon 2026**.

---

## 🐕 What It Does

1. **Such Upload** — drop a photo from your life in 2026
2. **Very Analyze** — Qwen3.5-Vision reads it and writes a 2016-era Doge-approved scene description
3. **Much Generate** — Wan2.6-i2v-Flash animates your photo in the style of a decade ago
4. **Wow** — you receive a short `.mp4` video + a **"2016 Vibe Score"** (0–100)

---

## 🖥️ Demo

> Live demo URL: `https://your-sas-ip-or-domain`

![App Screenshot](docs/screenshot.png)

---

## 🗂️ Project Structure

```
nostalgia-engine/
├── frontend/                  # Vue.js / React single-page app
│   ├── src/
│   │   ├── components/        # Upload, StatusPoller, VideoResult
│   │   ├── views/             # Landing, Processing, Result
│   │   └── App.vue / App.jsx
│   └── Dockerfile
│
├── backend/                   # Python 3.11 + FastAPI
│   ├── main.py                # API routes
│   ├── services/
│   │   ├── qwen.py            # Qwen3.5-Vision integration
│   │   ├── wan.py             # Wan2.6-i2v-Flash async job handling
│   │   └── oss.py             # OSS upload + signed URL generation
│   ├── requirements.txt
│   └── Dockerfile
│
├── infra/                     # OpenTofu infrastructure-as-code
│   ├── main.tf                # Root config — wires modules together
│   ├── variables.tf           # All input variable declarations
│   ├── outputs.tf             # Exposes SAS IP, OSS domain, app URLs
│   ├── terraform.tfvars.example
│   ├── .gitignore             # Excludes *.tfvars and state files
│   └── modules/
│       ├── sas/               # Simple Application Server instance + firewall
│       │   ├── main.tf        # Instance resource + cloud-init bootstrap
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── oss/               # Object Storage bucket + CORS + lifecycle
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
│
├── docs/                      # Project documentation
│   ├── ARCHITECTURE.md        # Full architecture, sequence diagrams, component breakdown
│   └── screenshot.png         # App screenshot for README
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧠 Architecture

```
User → Vue/React (SAS)
     → FastAPI Backend (SAS)
     → Qwen3.5-Vision        — analyzes photo, writes 2016-era prompt
     → Wan2.6-i2v-Flash      — generates nostalgic video (async, polled every 3–5s)
     → OSS                   — stores .mp4, returns signed URL
     → User sees video + Vibe Score
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full sequence diagram and component breakdown.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Alibaba Cloud account with:
  - **Simple Application Server (SAS)** instance (Ubuntu 22.04, 2 vCPU / 4 GB RAM recommended)
  - **Model Studio** API key (access to `qwen3.5-plus` and `wan2.6-i2v-flash`)
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

# OSS
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=nostalgia-engine-outputs
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_SIGNED_URL_EXPIRY=3600

# App
POLL_INTERVAL_SECONDS=4
MAX_POLL_ATTEMPTS=60
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
  -d '{"image_base64": "<base64>", "filename": "photo.jpg"}'
```

**Response `202 Accepted`:**
```json
{
  "job_id": "wanx-job-abc123",
  "status": "pending",
  "vibe_score": 78,
  "scene_description": "A casual outdoor moment remixed into 2016 VSCO aesthetic..."
}
```

---

### `GET /api/status/{job_id}`

Poll for job completion.

```bash
curl http://localhost:8000/api/status/wanx-job-abc123
```

**Response on success:**
```json
{
  "job_id": "wanx-job-abc123",
  "status": "success",
  "video_url": "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/wanx-job-abc123.mp4?Expires=...",
  "vibe_score": 78
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue.js 3 / React 18 |
| Backend | Python 3.11 + FastAPI |
| Vision AI | Qwen3.5-Vision (Alibaba Cloud Model Studio) |
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
| `OSS_BUCKET_NAME` | OSS bucket for video output | — |
| `OSS_ENDPOINT` | OSS regional endpoint | `oss-cn-hangzhou.aliyuncs.com` |
| `OSS_SIGNED_URL_EXPIRY` | Signed URL validity in seconds | `3600` |
| `POLL_INTERVAL_SECONDS` | Wan job polling frequency | `4` |
| `MAX_POLL_ATTEMPTS` | Max polling attempts before timeout | `60` |

---

## 🧪 Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev        # Vue: vite dev server on :5173
```

---

## 📦 Deploying Infrastructure with OpenTofu

All cloud resources — the SAS instance, OSS bucket, CORS rules, firewall ports, and lifecycle policies — are declared in `infra/` and provisioned with [OpenTofu](https://opentofu.org/).

### Prerequisites

- [OpenTofu ≥ 1.6](https://opentofu.org/docs/intro/install/) installed locally
- Alibaba Cloud credentials with ECS / OSS / SAS permissions

### 1. Configure variables

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — fill in your access keys, bucket name, SSH key pair, etc.
```

### 2. Initialise providers

```bash
tofu init
```

### 3. Preview the plan

```bash
tofu plan
```

### 4. Apply

```bash
tofu apply
```

OpenTofu will provision:
- **OSS bucket** (`modules/oss`) — private bucket with CORS, 7-day video expiry lifecycle
- **SAS instance** (`modules/sas`) — Ubuntu 22.04, Docker pre-installed via cloud-init, app cloned and started automatically
- **Firewall rules** — ports 22 (SSH), 80 (frontend), 8000 (API) opened

On completion, outputs are printed:

```
app_url       = "http://<sas-public-ip>"
api_url       = "http://<sas-public-ip>:8000"
oss_bucket    = "nostalgia-engine-outputs-yourname"
```

### 5. Destroy (teardown)

```bash
tofu destroy
```

> **State management:** For team use, uncomment the `backend "oss"` block in `infra/main.tf` to store Terraform state remotely in OSS.

---

## 🪪 License

MIT — see [`LICENSE`](LICENSE) for details.

---

## 🙌 Acknowledgements

- [Alibaba Cloud Model Studio](https://www.alibabacloud.com/product/modelstudio) — Qwen3.5-Vision & Wan2.6-i2v-Flash
- [Alibaba Cloud OSS](https://www.alibabacloud.com/product/oss)
- [Alibaba Cloud SAS](https://www.alibabacloud.com/product/swas)
- Built with [Qoder AI](https://qoder.ai) agentic coding tools

---

*Alibaba Cloud AI × Creativity Hackathon 2026 — Such Nostalgia. Very 2016. Wow. 🐕*
