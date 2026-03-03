<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])

const isDragging = ref(false)
const error = ref('')
const fileInput = ref(null)

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_MB = 10

function handleFile(file) {
  error.value = ''

  if (!ACCEPTED_TYPES.includes(file.type)) {
    error.value = 'Such wrong format. Only JPEG, PNG, or WebP. Wow.'
    return
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    error.value = `Such big. Very ${MAX_SIZE_MB}MB limit. Much compress.`
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    const base64 = dataUrl.split(',')[1]
    emit('file-selected', { base64, filename: file.name, dataUrl })
  }
  reader.readAsDataURL(file)
}

function onDragOver(e) {
  e.preventDefault()
  isDragging.value = true
}
function onDragLeave() {
  isDragging.value = false
}
function onDrop(e) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) handleFile(file)
}
function onInputChange(e) {
  const file = e.target.files[0]
  if (file) handleFile(file)
  // Reset so the same file can be re-selected
  e.target.value = ''
}
function openPicker() {
  fileInput.value?.click()
}
</script>

<template>
  <div
    class="upload-zone"
    :class="{ 'upload-zone--dragging': isDragging }"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="openPicker"
    role="button"
    tabindex="0"
    @keydown.enter="openPicker"
    @keydown.space.prevent="openPicker"
    aria-label="Upload photo"
  >
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="upload-zone__input"
      @change="onInputChange"
    />

    <div class="upload-zone__icon">☁</div>
    <p class="upload-zone__headline">Drop your photo here</p>
    <p class="upload-zone__sub">or click to browse</p>
    <p class="upload-zone__hint">JPEG · PNG · WebP · max 10 MB</p>

    <p v-if="error" class="upload-zone__error">{{ error }}</p>
  </div>
</template>

<style scoped>
.upload-zone {
  width: 100%;
  min-height: 220px;
  border: 2.5px dashed var(--gold);
  border-radius: var(--radius-lg);
  background: rgba(253,248,242,0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
  padding: 40px 24px;
  position: relative;
  outline: none;
}

.upload-zone:hover,
.upload-zone:focus-visible {
  border-color: var(--amber);
  background: rgba(253,248,242,0.92);
  transform: scale(1.01);
}

.upload-zone--dragging {
  border-color: var(--amber);
  background: rgba(212,165,90,0.12);
  transform: scale(1.02);
  box-shadow: 0 0 0 4px rgba(212,165,90,0.2);
}

.upload-zone__input {
  display: none;
}

.upload-zone__icon {
  font-size: 3.5rem;
  line-height: 1;
  opacity: 0.5;
  transition: opacity 0.2s, transform 0.2s;
}

.upload-zone:hover .upload-zone__icon,
.upload-zone--dragging .upload-zone__icon {
  opacity: 0.8;
  transform: translateY(-4px);
}

.upload-zone__headline {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--amber-dark);
  margin-top: 4px;
}

.upload-zone__sub {
  font-size: 0.95rem;
  color: var(--text-mid);
}

.upload-zone__hint {
  font-size: 0.8rem;
  color: var(--text-light);
  margin-top: 4px;
  letter-spacing: 0.03em;
}

.upload-zone__error {
  margin-top: 10px;
  font-size: 0.9rem;
  color: var(--red);
  font-weight: 600;
  text-align: center;
}
</style>
