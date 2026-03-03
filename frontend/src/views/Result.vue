<script setup>
import VideoResult from '../components/VideoResult.vue'

defineProps({
  videoUrl:         { type: String, required: true },
  vibeScore:        { type: Number, required: true },
  sceneDescription: { type: String, default: '' },
  imageDataUrl:     { type: String, default: '' },
})

defineEmits(['restart'])
</script>

<template>
  <div class="result-view">
    <!-- ── Header ── -->
    <header class="result-view__header">
      <div class="confetti-row" aria-hidden="true">
        <span>✨</span><span>🐕</span><span>📷</span>
        <span>✨</span><span>🌅</span><span>📸</span><span>✨</span>
      </div>
      <h1 class="result-title">Wow. Such 2016. Many nostalgia.</h1>
      <p class="result-sub">
        Your photo has been rewound to peak 2016 energy.
      </p>
    </header>

    <!-- ── Main content ── -->
    <main class="result-view__main">
      <!-- ── Video + score ── -->
      <VideoResult
        :video-url="videoUrl"
        :vibe-score="vibeScore"
      />

      <!-- ── Scene description ── -->
      <div v-if="sceneDescription" class="scene-card">
        <p class="scene-card__label">Qwen's 2016 Reframe</p>
        <blockquote class="scene-card__text">
          "{{ sceneDescription }}"
        </blockquote>
        <p class="scene-card__credit">via Qwen3.5-Vision</p>
      </div>

      <!-- ── Source photo comparison ── -->
      <div v-if="imageDataUrl" class="compare-row">
        <div class="compare-item">
          <img :src="imageDataUrl" alt="Original 2026 photo" class="compare-img" />
          <p class="compare-label">Your 2026 photo</p>
        </div>
        <div class="compare-arrow">→</div>
        <div class="compare-item compare-item--video">
          <div class="compare-video-badge">
            <span>▶</span>
          </div>
          <p class="compare-label">2016 Nostalgia clip</p>
        </div>
      </div>

      <!-- ── Actions ── -->
      <div class="actions">
        <a
          :href="videoUrl"
          download="nostalgia-2016.mp4"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-primary"
        >
          ↓ Download .mp4
        </a>
        <button class="btn-ghost" @click="$emit('restart')">
          🐕 Again! New photo
        </button>
      </div>

      <!-- ── Doge footer quote ── -->
      <div class="doge-quote">
        <span class="meme-word" style="color:#c8832a;font-size:1rem;transform:rotate(-4deg);display:inline-block;">much wow</span>
        &nbsp;·&nbsp;
        <span class="meme-word" style="color:#7a5232;font-size:0.9rem;transform:rotate(3deg);display:inline-block;">very rewind</span>
        &nbsp;·&nbsp;
        <span class="meme-word" style="color:#d4a55a;font-size:1.05rem;transform:rotate(-2deg);display:inline-block;">such nostalgia</span>
      </div>
    </main>

    <!-- ── Footer ── -->
    <footer class="result-view__footer">
      Powered by Qwen3.5-Vision &amp; Wan2.6-i2v-Flash · Alibaba Cloud
    </footer>
  </div>
</template>

<style scoped>
.result-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Header ── */
.result-view__header {
  text-align: center;
  padding: 36px 24px 8px;
}

.confetti-row {
  font-size: 1.8rem;
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 12px;
  animation: confetti-bounce 1.2s ease both;
}

.confetti-row span {
  display: inline-block;
  animation: confetti-bounce 0.8s ease both;
}
.confetti-row span:nth-child(2)  { animation-delay: 0.05s; }
.confetti-row span:nth-child(3)  { animation-delay: 0.10s; }
.confetti-row span:nth-child(4)  { animation-delay: 0.15s; }
.confetti-row span:nth-child(5)  { animation-delay: 0.20s; }
.confetti-row span:nth-child(6)  { animation-delay: 0.25s; }
.confetti-row span:nth-child(7)  { animation-delay: 0.30s; }

@keyframes confetti-bounce {
  0%   { transform: translateY(-20px); opacity: 0; }
  60%  { transform: translateY(4px); }
  100% { transform: translateY(0); opacity: 1; }
}

.result-title {
  font-size: clamp(1.6rem, 4vw, 2.6rem);
  font-weight: 900;
  color: var(--brown);
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.result-sub {
  font-size: 1rem;
  color: var(--text-mid);
}

/* ── Main ── */
.result-view__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 24px 24px 40px;
}

/* ── Scene card ── */
.scene-card {
  width: 100%;
  max-width: 480px;
  background: var(--bg-card);
  border: 1px solid rgba(212,165,90,0.25);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow);
}

.scene-card__label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-light);
  margin-bottom: 10px;
}

.scene-card__text {
  font-size: 0.92rem;
  color: var(--text-mid);
  line-height: 1.7;
  font-style: italic;
  border-left: 3px solid var(--gold);
  padding-left: 12px;
  margin: 0 0 8px;
}

.scene-card__credit {
  font-size: 0.75rem;
  color: var(--text-light);
  text-align: right;
}

/* ── Compare row ── */
.compare-row {
  display: flex;
  align-items: center;
  gap: 20px;
  max-width: 480px;
  width: 100%;
}

.compare-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.compare-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radius);
  box-shadow: 0 4px 16px rgba(92,48,16,0.15);
  filter: saturate(1.08) sepia(0.1);
}

.compare-item--video {
  /* Placeholder for video thumbnail */
}

.compare-video-badge {
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--radius);
  background: linear-gradient(135deg, #2c1a08 0%, #5c3010 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: rgba(255,252,240,0.7);
  box-shadow: 0 4px 16px rgba(92,48,16,0.25);
}

.compare-label {
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: 600;
  text-align: center;
}

.compare-arrow {
  font-size: 1.5rem;
  color: var(--gold);
  font-weight: 700;
  flex-shrink: 0;
}

/* ── Actions ── */
.actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

/* ── Doge quote ── */
.doge-quote {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0.7;
  padding: 4px;
}

/* ── Footer ── */
.result-view__footer {
  padding: 16px 24px;
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-light);
  border-top: 1px solid rgba(212,165,90,0.15);
}

/* ── Responsive ── */
@media (max-width: 480px) {
  .compare-arrow { display: none; }
  .compare-row {
    flex-direction: column;
  }
  .compare-item { max-width: 240px; }
  .actions { flex-direction: column; align-items: stretch; }
}
</style>
