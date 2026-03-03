<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  videoUrl:  { type: String, required: true },
  vibeScore: { type: Number, required: true },
})

const displayScore = ref(0)
const videoRef = ref(null)

// Ease-out cubic function
function easeOut(t) {
  return 1 - Math.pow(1 - t, 3)
}

// Animated counter 0 → vibeScore over ~1.8s
onMounted(() => {
  const duration = 1800
  let startTs = null

  function step(ts) {
    if (!startTs) startTs = ts
    const progress = Math.min((ts - startTs) / duration, 1)
    displayScore.value = Math.round(easeOut(progress) * props.vibeScore)
    if (progress < 1) requestAnimationFrame(step)
  }

  // Small delay so the view has rendered
  setTimeout(() => requestAnimationFrame(step), 300)
})

// Vibe tier for colour / label
function vibeTier(score) {
  if (score >= 85) return { label: 'Peak 2016 Energy',  cls: 'tier--peak'   }
  if (score >= 65) return { label: 'Very VSCO',          cls: 'tier--high'   }
  if (score >= 45) return { label: 'Such Nostalgic',     cls: 'tier--mid'    }
  return                 { label: 'Barely Retro',        cls: 'tier--low'    }
}
</script>

<template>
  <div class="video-result">
    <!-- ── Video player ── -->
    <div class="player-frame">
      <!-- Filter label overlay -->
      <div class="player-frame__tag">A4 · HB2</div>

      <video
        ref="videoRef"
        :src="videoUrl"
        class="player"
        autoplay
        loop
        muted
        playsinline
        controls
      />

      <!-- Vignette overlay -->
      <div class="player-frame__vignette" />
    </div>

    <!-- ── Vibe Score ── -->
    <div class="score-block">
      <p class="score-block__eyebrow">2016 Vibe Score</p>

      <div class="score-dial">
        <svg viewBox="0 0 120 70" class="score-arc" aria-hidden="true">
          <!-- Track -->
          <path
            d="M 10 65 A 50 50 0 0 1 110 65"
            fill="none"
            stroke="rgba(212,165,90,0.2)"
            stroke-width="10"
            stroke-linecap="round"
          />
          <!-- Fill (dasharray animated via CSS var) -->
          <path
            d="M 10 65 A 50 50 0 0 1 110 65"
            fill="none"
            :stroke="displayScore >= 65 ? '#c07830' : displayScore >= 45 ? '#d4a55a' : '#a07850'"
            stroke-width="10"
            stroke-linecap="round"
            :stroke-dasharray="`${(displayScore / 100) * 157} 157`"
            class="score-arc__fill"
          />
        </svg>
        <div class="score-number">{{ displayScore }}</div>
      </div>

      <div
        class="score-tier"
        :class="vibeTier(displayScore).cls"
      >
        {{ vibeTier(displayScore).label }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  width: 100%;
}

/* ── Player ── */
.player-frame {
  position: relative;
  width: 100%;
  max-width: 480px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(92,48,16,0.28);
  background: #111;
}

.player {
  width: 100%;
  display: block;
  /* Warm nostalgic filter */
  filter: saturate(1.12) contrast(1.06) sepia(0.1) brightness(1.03);
}

.player-frame__tag {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 2;
  font-family: Impact, 'Arial Black', Arial, sans-serif;
  font-style: italic;
  font-size: 0.75rem;
  color: rgba(255,252,240,0.85);
  letter-spacing: 0.12em;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

.player-frame__vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(
    ellipse at center,
    transparent 55%,
    rgba(30,12,4,0.45) 100%
  );
}

/* ── Score dial ── */
.score-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 100%;
  max-width: 240px;
}

.score-block__eyebrow {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-light);
}

.score-dial {
  position: relative;
  width: 160px;
}

.score-arc {
  width: 100%;
  height: auto;
  overflow: visible;
}

.score-arc__fill {
  transition: stroke-dasharray 0.05s;
}

.score-number {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--amber-dark);
  line-height: 1;
  letter-spacing: -0.03em;
  min-width: 3ch;
  text-align: center;
}

.score-tier {
  font-size: 0.88rem;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 20px;
  letter-spacing: 0.04em;
}

.tier--peak { background: rgba(192,120,48,0.18); color: var(--amber); }
.tier--high { background: rgba(212,165,90,0.18); color: var(--gold);  }
.tier--mid  { background: rgba(160,120,80,0.15); color: var(--text-mid); }
.tier--low  { background: rgba(160,120,80,0.1);  color: var(--text-light); }
</style>
