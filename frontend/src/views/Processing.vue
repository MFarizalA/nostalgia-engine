<script setup>
import { ref, computed } from 'vue'
import StatusPoller from '../components/StatusPoller.vue'

const props = defineProps({
  jobId:            { type: String,  required: true },
  vibeScore:        { type: Number,  default: null },
  sceneDescription: { type: String,  default: '' },
  imageDataUrl:     { type: String,  default: '' },
})

const emit = defineEmits(['complete', 'failed'])

const currentStatus = ref('pending')
const errorMessage = ref('')

// Status label per job state
const statusMessages = {
  pending:    'Much generate… please wait',
  processing: 'Very rewind… still cooking',
  success:    'Wow. Such 2016. Many nostalgia. 🐕',
  failed:     'Such fail. Very sad. Much retry.',
}

const statusLabel = computed(() => statusMessages[currentStatus.value] ?? 'Working on it…')

// Progress dots cycling animation
const DOT_COUNT = 8
const activeDot = ref(0)
let dotInterval = setInterval(() => {
  activeDot.value = (activeDot.value + 1) % DOT_COUNT
}, 350)

function onStatusUpdate(data) {
  currentStatus.value = data.status
}

function onComplete(data) {
  clearInterval(dotInterval)
  emit('complete', data)
}

function onFailed(msg) {
  clearInterval(dotInterval)
  currentStatus.value = 'failed'
  errorMessage.value = msg || 'Unknown error'
  // Give user a moment to read the error, then bubble up
  setTimeout(() => emit('failed'), 3500)
}

import { onUnmounted } from 'vue'
onUnmounted(() => clearInterval(dotInterval))
</script>

<template>
  <div class="processing">
    <StatusPoller
      :job-id="jobId"
      @status-update="onStatusUpdate"
      @complete="onComplete"
      @failed="onFailed"
    />

    <div class="processing__inner">
      <!-- ── Left: photo preview ── -->
      <div class="photo-panel">
        <div class="polaroid">
          <img
            v-if="imageDataUrl"
            :src="imageDataUrl"
            alt="Your uploaded photo"
            class="polaroid__img"
          />
          <div v-else class="polaroid__placeholder">🖼</div>
          <div class="polaroid__caption">2016-ifying…</div>
        </div>

        <!-- Decorative filter badge -->
        <div class="filter-badge">
          <span>HB2</span>
          <span class="filter-badge__ring"></span>
        </div>
      </div>

      <!-- ── Right: status panel ── -->
      <div class="status-panel">
        <!-- Doge spinner -->
        <div class="doge-spinner">
          <span class="doge-spinner__emoji">🐕</span>
        </div>

        <!-- Status message -->
        <p
          class="status-msg"
          :class="`status-msg--${currentStatus}`"
        >
          {{ statusLabel }}
        </p>

        <!-- Progress dots -->
        <div v-if="currentStatus !== 'failed'" class="dots-row">
          <span
            v-for="i in DOT_COUNT"
            :key="i"
            class="dot"
            :class="{ 'dot--active': activeDot === i - 1 }"
          />
        </div>

        <!-- Vibe score preview (returned from initial 202) -->
        <div v-if="vibeScore !== null" class="vibe-preview">
          <span class="vibe-preview__label">2016 Vibe Score</span>
          <span class="vibe-preview__score">{{ vibeScore }}</span>
          <span class="vibe-preview__max">/100</span>
        </div>

        <!-- Scene description preview -->
        <blockquote v-if="sceneDescription" class="scene-desc">
          "{{ sceneDescription }}"
        </blockquote>

        <!-- Stage tags -->
        <div class="stage-tags">
          <span
            class="tag"
            :class="{ 'tag--done': currentStatus !== 'pending' }"
          >
            Qwen Vision
          </span>
          <span class="tag__arrow">→</span>
          <span
            class="tag"
            :class="{
              'tag--active': currentStatus === 'processing',
              'tag--done':   currentStatus === 'success'
            }"
          >
            Wan i2v
          </span>
          <span class="tag__arrow">→</span>
          <span
            class="tag"
            :class="{ 'tag--active': currentStatus === 'success' }"
          >
            OSS Storage
          </span>
        </div>

        <!-- Error state -->
        <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.processing {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.processing__inner {
  display: flex;
  gap: 48px;
  align-items: flex-start;
  max-width: 800px;
  width: 100%;
}

/* ── Polaroid ── */
.photo-panel {
  position: relative;
  flex-shrink: 0;
}

.polaroid {
  background: #fefcf5;
  padding: 12px 12px 40px;
  box-shadow: 0 8px 32px rgba(92,48,16,0.22), 0 2px 6px rgba(0,0,0,0.08);
  border-radius: 3px;
  width: 220px;
  transform: rotate(-2.5deg);
  transition: transform 0.4s ease;
}
.polaroid:hover { transform: rotate(0deg) scale(1.03); }

.polaroid__img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
  border-radius: 2px;
  filter: saturate(1.08) contrast(1.06) sepia(0.12) brightness(1.04);
  /* Pulsing glow to indicate processing */
  animation: glow 2.5s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 0 rgba(212,165,90,0); }
  50%       { box-shadow: 0 0 20px rgba(212,165,90,0.5); }
}

.polaroid__placeholder {
  width: 196px;
  height: 196px;
  background: var(--bg-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  border-radius: 2px;
}

.polaroid__caption {
  text-align: center;
  margin-top: 10px;
  font-size: 0.85rem;
  color: var(--text-light);
  font-style: italic;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.filter-badge {
  position: absolute;
  bottom: -14px;
  right: -14px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-dark) 100%);
  color: var(--white);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(139,78,24,0.4);
  z-index: 2;
}

.filter-badge__ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid rgba(212,165,90,0.5);
  animation: ring-pulse 2s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% { transform: scale(1);    opacity: 0.7; }
  50%       { transform: scale(1.15); opacity: 0.3; }
}

/* ── Status panel ── */
.status-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 8px;
}

/* Doge spinner */
.doge-spinner {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f7ead8 0%, #ede0c4 100%);
  box-shadow: 0 4px 16px rgba(92,48,16,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.doge-spinner__emoji {
  font-size: 2rem;
  animation: doge-spin 1.8s ease-in-out infinite;
  display: block;
}

@keyframes doge-spin {
  0%   { transform: rotate(0deg)   scale(1); }
  25%  { transform: rotate(-8deg)  scale(1.05); }
  75%  { transform: rotate(8deg)   scale(1.05); }
  100% { transform: rotate(0deg)   scale(1); }
}

/* Status message */
.status-msg {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--amber-dark);
  line-height: 1.4;
}
.status-msg--success { color: var(--green); }
.status-msg--failed  { color: var(--red); }

/* Dots */
.dots-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--bg-2);
  border: 1.5px solid var(--gold);
  transition: background 0.2s, transform 0.2s;
}
.dot--active {
  background: var(--amber);
  transform: scale(1.4);
  box-shadow: 0 0 6px rgba(192,120,48,0.5);
}

/* Vibe score preview */
.vibe-preview {
  display: flex;
  align-items: baseline;
  gap: 4px;
  background: rgba(212,165,90,0.12);
  border: 1px solid rgba(212,165,90,0.3);
  border-radius: 10px;
  padding: 10px 16px;
  width: fit-content;
}
.vibe-preview__label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-light);
  margin-right: 8px;
}
.vibe-preview__score {
  font-size: 2rem;
  font-weight: 900;
  color: var(--amber-dark);
  line-height: 1;
}
.vibe-preview__max {
  font-size: 0.9rem;
  color: var(--text-light);
  font-weight: 600;
}

/* Scene description */
.scene-desc {
  font-size: 0.88rem;
  color: var(--text-mid);
  line-height: 1.65;
  border-left: 3px solid var(--gold);
  padding-left: 12px;
  font-style: italic;
  margin: 0;
}

/* Stage tags */
.stage-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.tag {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--bg-2);
  color: var(--text-light);
  border: 1.5px solid rgba(212,165,90,0.2);
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}
.tag--active {
  background: rgba(192,120,48,0.15);
  color: var(--amber);
  border-color: var(--amber);
  animation: tag-pulse 1.5s ease-in-out infinite;
}
.tag--done {
  background: rgba(107,158,94,0.12);
  color: var(--green);
  border-color: var(--green);
}
.tag__arrow { color: var(--gold); font-size: 0.9rem; }

@keyframes tag-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.65; }
}

.error-msg {
  font-size: 0.9rem;
  color: var(--red);
  font-weight: 600;
}

/* ── Responsive ── */
@media (max-width: 600px) {
  .processing__inner {
    flex-direction: column;
    align-items: center;
  }
  .polaroid { transform: rotate(0deg); }
}
</style>
