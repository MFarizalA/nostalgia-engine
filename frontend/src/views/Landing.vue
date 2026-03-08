<script setup>
import { ref } from 'vue'
import UploadZone from '../components/UploadZone.vue'

const emit = defineEmits(['submitted'])

const imageData  = ref(null)   // { base64, filename, dataUrl }
const era        = ref(2016)
const festivity  = ref(null)   // null | 'cny' | 'ramadan' | 'eid'
const style      = ref(null)   // null | 'vsco' | 'grunge' | 'meme' | 'cine'
const loading    = ref(false)
const submitError = ref('')

const ERAS = [2010, 2012, 2014, 2016, 2018, 2020]

const FESTIVITIES = [
  { key: null,     icon: '✨', label: 'No theme',    tagline: 'Pure nostalgia' },
  { key: 'cny',    icon: '🧧', label: 'Lunar New Year', tagline: 'Gong Xi Fa Cai' },
  { key: 'ramadan',icon: '🌙', label: 'Ramadan',     tagline: 'Ramadan Kareem' },
  { key: 'eid',    icon: '🎊', label: 'Eid',         tagline: 'Eid Mubarak' },
]

const STYLES = [
  { key: null,     icon: '🎞️', label: 'Auto',        tagline: 'Let Qwen decide' },
  { key: 'vsco',   icon: '📸', label: 'VSCO',        tagline: 'Warm fade & grain' },
  { key: 'grunge', icon: '🌑', label: 'Grunge',      tagline: 'Dark & moody' },
  { key: 'meme',   icon: '😂', label: 'Meme-Heavy',  tagline: 'Maximum chaos' },
  { key: 'cine',   icon: '🎬', label: 'Cinemagraph', tagline: 'Film grain & flare' },
]

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
        filename:     imageData.value.filename,
        era:          era.value,
        festivity:    festivity.value,
        style:        style.value,
      }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `HTTP ${res.status}`)
    }

    const data = await res.json()
    emit('submitted', {
      jobId:            data.job_id,
      vibeScore:        data.vibe_score,
      sceneDescription: data.scene_description,
      imageDataUrl:     imageData.value.dataUrl,
      era:              era.value,
      festivity:        festivity.value,
      style:            style.value,
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
        <span class="meme-word meme-1" style="color:#c8832a;font-size:1.3rem;">wow</span>
        <span class="meme-word meme-2" style="color:#7a5232;font-size:1rem;">such filter</span>
        <span class="meme-word meme-3" style="color:#c8832a;font-size:1.15rem;">very VSCO</span>
        <span class="meme-word meme-4" style="color:#5c3010;font-size:0.95rem;">much pixel</span>
        <span class="meme-word meme-5" style="color:#d4a55a;font-size:1.2rem;">many nostalgia</span>
        <span class="meme-word meme-6" style="color:#8b4e18;font-size:0.9rem;">such rewind</span>
        <span class="meme-word meme-7" style="color:#c07830;font-size:1.05rem;">very {{ era }}</span>

        <div class="hero__doge">🐕</div>
        <h1 class="hero__title">Nostalgia Engine</h1>
        <p class="hero__tagline">
          Such {{ era }}.&nbsp; Very filter.&nbsp; Much AI.&nbsp; <strong>Wow.</strong>
        </p>
        <p class="hero__sub">
          Drop a photo, pick your era and vibe, and let Qwen + Wan rewind it to<br />
          peak internet nostalgia — VSCO cams, golden-hour selfies, and pure Doge energy.
        </p>
      </div>
    </header>

    <!-- ── Main ── -->
    <main class="landing__main">

      <!-- ── Step 1: Upload ── -->
      <div class="card">
        <p class="card__label">Step 1 — Upload your photo</p>
        <template v-if="!imageData">
          <UploadZone @file-selected="onFileSelected" />
        </template>
        <template v-else>
          <div class="uploaded-row">
            <div class="preview-thumb">
              <img :src="imageData.dataUrl" alt="preview" class="preview-img" />
            </div>
            <div class="uploaded-meta">
              <p class="preview-filename">{{ imageData.filename }}</p>
              <button class="btn-ghost btn-ghost--sm" @click="clearImage">← Change photo</button>
            </div>
          </div>
        </template>
      </div>

      <!-- ── Step 2: Era ── -->
      <div class="card">
        <p class="card__label">Step 2 — Pick your era</p>
        <div class="era-row">
          <button
            v-for="y in ERAS"
            :key="y"
            class="era-pill"
            :class="{ 'era-pill--active': era === y }"
            @click="era = y"
          >
            {{ y }}{{ y === 2016 ? ' ★' : '' }}
          </button>
        </div>
        <p class="selector-hint">{{ era }} internet culture will shape the AI's scene description and video style.</p>
      </div>

      <!-- ── Step 3: Festivity ── -->
      <div class="card">
        <p class="card__label">Step 3 — Festivity <span class="card__label--opt">(optional)</span></p>
        <div class="tile-grid">
          <button
            v-for="f in FESTIVITIES"
            :key="String(f.key)"
            class="tile"
            :class="{ 'tile--active': festivity === f.key }"
            @click="festivity = f.key"
          >
            <span class="tile__icon">{{ f.icon }}</span>
            <span class="tile__label">{{ f.label }}</span>
            <span class="tile__tagline">{{ f.tagline }}</span>
          </button>
        </div>
      </div>

      <!-- ── Step 4: Style ── -->
      <div class="card">
        <p class="card__label">Step 4 — Aesthetic style <span class="card__label--opt">(optional)</span></p>
        <div class="tile-grid tile-grid--5">
          <button
            v-for="s in STYLES"
            :key="String(s.key)"
            class="tile"
            :class="{ 'tile--active': style === s.key }"
            @click="style = s.key"
          >
            <span class="tile__icon">{{ s.icon }}</span>
            <span class="tile__label">{{ s.label }}</span>
            <span class="tile__tagline">{{ s.tagline }}</span>
          </button>
        </div>
      </div>

      <!-- ── Step 5: Confirm & Generate ── -->
      <div class="card" v-if="imageData">
        <p class="card__label">Step 5 — Confirm &amp; generate</p>
        <div class="confirm-row">
          <div class="confirm-summary">
            <span class="confirm-tag">📅 {{ era }}</span>
            <span v-if="festivity" class="confirm-tag">
              {{ FESTIVITIES.find(f => f.key === festivity)?.icon }}
              {{ FESTIVITIES.find(f => f.key === festivity)?.label }}
            </span>
            <span v-if="style" class="confirm-tag">
              {{ STYLES.find(s => s.key === style)?.icon }}
              {{ STYLES.find(s => s.key === style)?.label }}
            </span>
          </div>
          <div class="confirm-hint">
            Qwen3.5 will analyze your photo and generate a {{ era }}-era scene description + Vibe Score.
            Then Wan will animate it into a nostalgic short video.
          </div>
          <div class="confirm-actions">
            <button class="btn-primary" :disabled="loading" @click="onSubmit">
              <span v-if="!loading">Much Generate! →</span>
              <span v-else class="btn-loading">
                <span class="spinner"></span> Submitting…
              </span>
            </button>
          </div>
          <p v-if="submitError" class="submit-error">{{ submitError }}</p>
        </div>
      </div>

      <!-- ── How it works ── -->
      <div class="steps">
        <div class="step">
          <span class="step__num">1</span>
          <span class="step__text"><strong>Upload</strong> any photo</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">2</span>
          <span class="step__text"><strong>Pick</strong> era, vibe &amp; theme</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">3</span>
          <span class="step__text"><strong>Qwen</strong> reimagines it</span>
        </div>
        <span class="step__arrow">→</span>
        <div class="step">
          <span class="step__num">4</span>
          <span class="step__text"><strong>Wan</strong> animates the vibe 🐕</span>
        </div>
      </div>
    </main>

    <!-- ── Footer ── -->
    <footer class="landing__footer">
      Doge Nostalgia Engine &nbsp;·&nbsp; Alibaba Cloud AI x Creativity Hackathon 2026 &nbsp;·&nbsp; Qwen3.5 + Wan2.6-i2v-Flash &nbsp;·&nbsp; SAS hosted
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
  gap: 20px;
}

/* ── Card ── */
.card {
  width: 100%;
  max-width: 680px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 28px 32px;
  border: 1px solid rgba(212,165,90,0.2);
}

.card__label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-light);
  margin-bottom: 16px;
}

.card__label--opt {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  opacity: 0.7;
}

/* ── Upload preview ── */
.uploaded-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.preview-thumb {
  width: 80px;
  height: 80px;
  border-radius: var(--radius);
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(92,48,16,0.15);
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(1.1) contrast(1.05) sepia(0.1);
}

.uploaded-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-filename {
  font-size: 0.85rem;
  color: var(--text-light);
  font-weight: 600;
  word-break: break-all;
}

.btn-ghost--sm {
  font-size: 0.8rem;
  padding: 6px 12px;
}

/* ── Era pills ── */
.era-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.era-pill {
  padding: 8px 18px;
  border-radius: 999px;
  border: 2px solid rgba(212,165,90,0.35);
  background: transparent;
  color: var(--text-mid);
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
}

.era-pill:hover {
  border-color: var(--gold);
  color: var(--amber-dark);
}

.era-pill--active {
  background: var(--gold);
  border-color: var(--gold);
  color: var(--white);
  box-shadow: 0 2px 10px rgba(212,165,90,0.4);
}

.selector-hint {
  font-size: 0.8rem;
  color: var(--text-light);
  margin-top: 4px;
}

/* ── Tile grid (festivity / style) ── */
.tile-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.tile-grid--5 {
  grid-template-columns: repeat(5, 1fr);
}

.tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: var(--radius);
  border: 2px solid rgba(212,165,90,0.25);
  background: var(--bg);
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
  text-align: center;
}

.tile:hover {
  border-color: var(--gold);
  background: rgba(212,165,90,0.08);
}

.tile--active {
  border-color: var(--amber);
  background: rgba(212,165,90,0.15);
  box-shadow: 0 0 0 3px rgba(212,165,90,0.2);
}

.tile__icon {
  font-size: 1.6rem;
  line-height: 1;
}

.tile__label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text);
}

.tile__tagline {
  font-size: 0.68rem;
  color: var(--text-light);
  line-height: 1.3;
}

/* ── Confirm ── */
.confirm-row {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.confirm-summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.confirm-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(212,165,90,0.15);
  border: 1px solid rgba(212,165,90,0.3);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--amber-dark);
}

.confirm-hint {
  font-size: 0.85rem;
  color: var(--text-mid);
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  gap: 10px;
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

@keyframes spin { to { transform: rotate(360deg); } }

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
@media (max-width: 600px) {
  .tile-grid       { grid-template-columns: repeat(2, 1fr); }
  .tile-grid--5    { grid-template-columns: repeat(3, 1fr); }
  .step__arrow     { display: none; }
  .steps           { flex-direction: column; }
  .card            { padding: 20px; }
  .era-row         { gap: 8px; }
}
</style>
