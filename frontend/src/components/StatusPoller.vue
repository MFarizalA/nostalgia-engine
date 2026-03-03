<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  jobId: { type: String, required: true },
})

const emit = defineEmits(['status-update', 'complete', 'failed'])

const POLL_INTERVAL_MS = 4000
const MAX_ATTEMPTS = 60

const status = ref('pending')
const attempts = ref(0)
let intervalId = null

async function poll() {
  if (attempts.value >= MAX_ATTEMPTS) {
    emit('failed', 'Such timeout. Very long wait. Much retry.')
    clearInterval(intervalId)
    return
  }

  try {
    const res = await fetch(`/api/status/${props.jobId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()
    status.value = data.status
    emit('status-update', data)

    if (data.status === 'success') {
      clearInterval(intervalId)
      emit('complete', {
        videoUrl: data.video_url,
        vibeScore: data.vibe_score,
      })
    } else if (data.status === 'failed') {
      clearInterval(intervalId)
      emit('failed', data.error || 'Unknown error')
    }
  } catch (err) {
    // Network hiccup — keep polling
    console.warn('Poll error:', err.message)
  }

  attempts.value++
}

onMounted(() => {
  // Poll immediately, then on interval
  poll()
  intervalId = setInterval(poll, POLL_INTERVAL_MS)
})

onUnmounted(() => {
  clearInterval(intervalId)
})
</script>

<template>
  <!-- Renderless logic component — no visible output -->
  <slot :status="status" :attempts="attempts" />
</template>
