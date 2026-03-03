<script setup>
import { ref } from 'vue'
import Landing from './views/Landing.vue'
import Processing from './views/Processing.vue'
import Result from './views/Result.vue'

const view = ref('landing')

const jobState = ref({
  jobId: null,
  vibeScore: null,
  sceneDescription: null,
  videoUrl: null,
  imageDataUrl: null,
})

function onJobSubmitted(data) {
  jobState.value = { ...jobState.value, ...data }
  view.value = 'processing'
}

function onJobComplete(data) {
  jobState.value = { ...jobState.value, ...data }
  view.value = 'result'
}

function onJobFailed() {
  view.value = 'landing'
}

function restart() {
  jobState.value = {
    jobId: null,
    vibeScore: null,
    sceneDescription: null,
    videoUrl: null,
    imageDataUrl: null,
  }
  view.value = 'landing'
}
</script>

<template>
  <div class="app-shell">
    <Transition name="fade" mode="out-in">
      <Landing
        v-if="view === 'landing'"
        key="landing"
        @submitted="onJobSubmitted"
      />
      <Processing
        v-else-if="view === 'processing'"
        key="processing"
        :job-id="jobState.jobId"
        :vibe-score="jobState.vibeScore"
        :scene-description="jobState.sceneDescription"
        :image-data-url="jobState.imageDataUrl"
        @complete="onJobComplete"
        @failed="onJobFailed"
      />
      <Result
        v-else-if="view === 'result'"
        key="result"
        :video-url="jobState.videoUrl"
        :vibe-score="jobState.vibeScore"
        :scene-description="jobState.sceneDescription"
        :image-data-url="jobState.imageDataUrl"
        @restart="restart"
      />
    </Transition>
  </div>
</template>

<style>
/* ── Global reset & custom properties ── */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg:          #f5ede0;
  --bg-2:        #ede0cc;
  --bg-card:     #fdf8f2;
  --gold:        #d4a55a;
  --amber:       #c07830;
  --amber-dark:  #8b4e18;
  --brown:       #5c3010;
  --text:        #2c1a08;
  --text-mid:    #7a5232;
  --text-light:  #a07850;
  --green:       #6b9e5e;
  --red:         #c04840;
  --white:       #fefcf8;
  --shadow:      0 4px 24px rgba(92,48,16,0.13);
  --radius:      12px;
  --radius-lg:   20px;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  font-size: 16px;
  color: var(--text);
  background-color: var(--bg);
  /* Warm paper grain background */
  background-image:
    radial-gradient(circle at 20% 50%, rgba(212,165,90,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(192,120,48,0.06) 0%, transparent 40%),
    radial-gradient(circle at 60% 80%, rgba(212,165,90,0.05) 0%, transparent 50%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── View transition ── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Shared button styles ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-dark) 100%);
  color: var(--white);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  box-shadow: 0 4px 16px rgba(139,78,24,0.35);
  text-decoration: none;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139,78,24,0.4);
}
.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}
.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: transparent;
  color: var(--amber);
  font-size: 1rem;
  font-weight: 600;
  border: 2px solid var(--amber);
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.15s, color 0.15s, transform 0.15s;
}
.btn-ghost:hover {
  background: var(--amber);
  color: var(--white);
  transform: translateY(-1px);
}

/* ── Doge meme text utility ── */
.meme-word {
  font-family: Impact, 'Arial Black', Arial, sans-serif;
  font-style: italic;
  position: absolute;
  pointer-events: none;
  user-select: none;
  opacity: 0.55;
  letter-spacing: 0.01em;
  text-shadow: 1px 1px 0 rgba(0,0,0,0.18);
}

/* ── Scrollbar styling ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 4px; }
</style>
