<script setup>
import { ref } from 'vue'
import UploadZone from '../components/UploadZone.vue'

const emit = defineEmits(['submitted'])

const imageData = ref(null)  // { base64, filename, dataUrl }
const loading = ref(false)
const submitError = ref('')

function onFileSelected(data) {
  imageData.value = data
  submitError.value = ''
}

function clearImage() {
  imageData.value = null
  submitError.value = ''
}

async function onSubmit() {
  if (!imageData.value || loading.value) return
  loading.value = true
  submitError.value = ''

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: imageData.value.base64,
        filename: imageData.value.filename,
      }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `HTTP ${res.status}`)
    }

    const data = await res.json()
    // data: { job_id, status, vibe_score, scene_description }
    emit('submitted', {
      jobId: data.job_id,
      vibeScore: data.vibe_score,
      sceneDescription: data.scene_description,
      imageDataUrl: imageData.value.dataUrl,
    })
  } catch (err) {
    submitError.value = `Such fail. Very error. ${err.message}`
    loading.value = false
  }
}
</script>

<template>
  <div class="landing">
    <!-- ── Header ── -->
    <header class="landing__header">
      <div class="hero">
        <!-- Floating Doge meme words -->
        <span class="meme-word meme-1" style="color:#c8832a;font-size:1.3rem;">wow</span>
        <span class="meme-word meme-2" style="color:#7a5232;font-size:1rem;">such filter</span>
        <span class="meme-word meme-3" style="color:#c8832a;font-size:1.15rem;">very VSCO</span>
        <span class="meme-word meme-4" style="color:#5c3010;font-size:0.95rem;">much pixel</span>
        <span class="meme-word meme-5" style="color:#d4a55a;font-size:1.2rem;">many nostalgia</span>
        <span class="meme-word meme-6" style="color:#8b4e18;font-size:0.9rem;">such rewind</span>
        <span class="meme-word meme-7" style="color:#c07830;font-size:1.05rem;">very 2016</span>

        <div class="hero__doge">🐕</div>
        <h1 class="hero__title">Nostalgia Engine</h1>
        <p class="hero__tagline">
          Such 2016.&nbsp; Very filter.&nbsp; Much AI.&nbsp; <strong>Wow.</strong>
        </p>
        <p class="hero__sub">
          Drop a photo from your modern life and let Qwen + Wan rewind it to<br />
          peak 2016 — VSCO cams, golden-hour selfies, and pure Doge energy.
        </p>
      </div>
    </header>

    <!-- ── Main content ── -->
    <main class="landing__main">
      <div class="card">
        <!-- Upload state -->
        <template v-if="!imageData">
          <p class="card__label">Step 1 — Upload your photo</p>
          <UploadZone @file-selected="onFileSelected" />
        </template>

        <!-- Preview + submit state -->
        <template v-else>
          <p class="card__label">Step 2 — Confirm &amp; generate</p>

          <div class="preview-area">
            <div class="preview-frame">
              <img :src="imageData.dataUrl" alt="Your photo" class="preview-img" />
              <div class="preview-overlay">
                <span class="preview-filter-tag">A4</span>
              </div>
            </div>
            <div class="preview-meta">
              <p class="preview-filename">{{ imageData.filename }}</p>
              <p class="preview-hint">
                Qwen3.5-Vision will analyze this photo and generate a<br />
                2016-era scene description + Vibe Score. Then Wan2.6-i2v-Flash<br />
                will animate it into a nostalgic short video.
              </p>
              <div class="preview-actions">
                <button class="btn-primary" :disabled="loading" @click="onSubmit">
                  <span v-if="!loading">Much Generate! →</span>
                  <span v-else class="btn-loading">
                    <span class="spinner"></span> Submitting…
                  </span>
                </button>
                <button class="btn-ghost" :disabled="loading" @click="clearImage">
                  ← Different photo
                </button>
              </div>
              <p v-if="submitError" class="submit-error">{{ submitError }}</p>
            </div>
          </div>
        </template>
      </div>

      <!-- How it works -->
      <div class="steps">
        <div class="step">
          <span class="step__num">1</span>
          <span class="step__text"><strong>Upload</strong> any photo</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">2</span>
          <span class="step__text"><strong>Qwen</strong> reimagines it in 2016</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">3</span>
          <span class="step__text"><strong>Wan</strong> animates the vibe</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">4</span>
          <span class="step__text"><strong>Wow.</strong> Your 2016 video 🐕</span>
        </div>
      </div>
    </main>

    <!-- ── Footer ── -->
    <footer class="landing__footer">
      Powered by Qwen3.5-Vision &amp; Wan2.6-i2v-Flash on Alibaba Cloud
      &nbsp;·&nbsp; Alibaba Cloud AI × Creativity Hackathon 2026
    </footer>
  </div>
</template>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Header / Hero ── */
.landing__header {
  padding: 48px 24px 32px;
}

.hero {
  position: relative;
  text-align: center;
  max-width: 680px;
  margin: 0 auto;
  padding: 16px;
}

.hero__doge {
  font-size: 5rem;
  line-height: 1;
  filter: drop-shadow(0 4px 12px rgba(139,78,24,0.25));
  margin-bottom: 12px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-8px); }
}

.hero__title {
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  color: var(--brown);
  text-shadow: 2px 2px 0 rgba(212,165,90,0.4);
  margin-bottom: 8px;
}

.hero__tagline {
  font-size: 1.2rem;
  color: var(--amber);
  font-weight: 600;
  margin-bottom: 12px;
}

.hero__sub {
  font-size: 0.95rem;
  color: var(--text-mid);
  line-height: 1.7;
}

/* Floating meme text positions */
.meme-1 { top: 10px;  left: 8%;  transform: rotate(-12deg); }
.meme-2 { top: 25px;  right: 6%; transform: rotate(9deg);   }
.meme-3 { bottom: 30px; left: 4%; transform: rotate(-7deg); }
.meme-4 { top: 55%;  right: 4%; transform: rotate(14deg);  }
.meme-5 { bottom: 10px; right: 8%; transform: rotate(-5deg); }
.meme-6 { top: 40%;  left: 2%;  transform: rotate(11deg);  }
.meme-7 { bottom: 50px; left: 12%; transform: rotate(-9deg); }

/* ── Main ── */
.landing__main {
  flex: 1;
  padding: 0 24px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

/* ── Card ── */
.card {
  width: 100%;
  max-width: 640px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 32px;
  border: 1px solid rgba(212,165,90,0.2);
}

.card__label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-light);
  margin-bottom: 20px;
}

/* ── Preview ── */
.preview-area {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.preview-frame {
  position: relative;
  width: 180px;
  min-width: 180px;
  aspect-ratio: 1;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(92,48,16,0.2);
  flex-shrink: 0;
  background: #111;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* Simulate VSCO A4 warm filter */
  filter: saturate(1.1) contrast(1.05) sepia(0.15) brightness(1.05);
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 60%,
    rgba(139,78,24,0.35) 100%
  );
}

.preview-filter-tag {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(255,252,240,0.9);
  letter-spacing: 0.1em;
  font-style: italic;
}

.preview-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-filename {
  font-size: 0.85rem;
  color: var(--text-light);
  font-weight: 600;
  word-break: break-all;
}

.preview-hint {
  font-size: 0.85rem;
  color: var(--text-mid);
  line-height: 1.6;
}

.preview-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2.5px solid rgba(255,252,240,0.4);
  border-top-color: var(--white);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.submit-error {
  font-size: 0.85rem;
  color: var(--red);
  font-weight: 600;
}

/* ── Steps row ── */
.steps {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 720px;
  width: 100%;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border: 1px solid rgba(212,165,90,0.25);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.88rem;
  color: var(--text-mid);
  box-shadow: 0 2px 8px rgba(92,48,16,0.07);
}

.step__num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--gold);
  color: var(--white);
  font-size: 0.78rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step__arrow {
  color: var(--gold);
  font-size: 1.2rem;
  font-weight: 700;
}

/* ── Footer ── */
.landing__footer {
  padding: 16px 24px;
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-light);
  border-top: 1px solid rgba(212,165,90,0.15);
}

/* ── Responsive ── */
@media (max-width: 520px) {
  .preview-area {
    flex-direction: column;
    align-items: center;
  }
  .preview-frame {
    width: 100%;
    max-width: 240px;
  }
  .step__arrow { display: none; }
  .steps { flex-direction: column; }
  .card { padding: 20px; }
}
</style>
