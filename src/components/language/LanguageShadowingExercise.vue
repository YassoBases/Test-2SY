<template>
  <div class="shadow-exercise rounded-lg pa-3" dir="ltr">
    <div class="d-flex align-center justify-space-between gap-2 mb-2 flex-wrap">
      <p class="text-body-2 font-weight-medium mb-0">{{ target }}</p>
      <div class="d-flex gap-2">
        <v-btn size="small" variant="tonal" color="secondary" prepend-icon="mdi-volume-high" @click="listen">
          Listen
        </v-btn>
        <v-btn
          size="small"
          :color="recording ? 'error' : 'primary'"
          :variant="recording ? 'flat' : 'tonal'"
          :loading="processing"
          :prepend-icon="recording ? 'mdi-stop' : 'mdi-microphone'"
          @click="recording ? stopRecording() : startRecording()"
        >
          {{ recording ? 'Stop' : 'Repeat' }}
        </v-btn>
      </div>
    </div>

    <div v-if="result" class="mt-2">
      <div class="d-flex align-center gap-2 mb-1 flex-wrap">
        <v-chip size="x-small" :color="result.passed ? 'success' : 'warning'" variant="flat">
          {{ result.passed ? 'Great match!' : 'Keep practicing' }}
        </v-chip>
        <span class="text-caption text-medium-emphasis">Match {{ result.similarity }}% · Pronunciation {{ result.overall_score }}/100</span>
      </div>
      <p v-if="result.transcript" class="text-caption text-medium-emphasis mb-1">You said: {{ result.transcript }}</p>
      <div v-if="weakWords.length" class="d-flex flex-wrap gap-1 mb-1">
        <v-chip
          v-for="w in weakWords"
          :key="w.word"
          size="x-small"
          color="warning"
          variant="tonal"
          :title="w.issue || 'needs practice'"
        >
          {{ w.word }}
        </v-chip>
      </div>
      <p v-if="result.note" class="text-caption mb-0">{{ result.note }}</p>
    </div>

    <p v-if="error" class="text-caption text-error mb-0 mt-1">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { submitShadow } from '../../api/language.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  target: { type: String, required: true },
})

const recording = ref(false)
const processing = ref(false)
const result = ref(null)
const error = ref('')

let mediaRecorder = null
let chunks = []
let stream = null

const weakWords = computed(() => (result.value?.words || []).filter((w) => w.weak))

function listen() {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(props.target)
  u.lang = 'en-US'
  u.rate = 0.95
  window.speechSynthesis.speak(u)
}

function pickMime() {
  const candidates = ['audio/webm', 'audio/mp4', 'audio/ogg']
  for (const t of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported?.(t)) return t
  }
  return ''
}

async function startRecording() {
  error.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    const mime = pickMime()
    mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size) chunks.push(e.data)
    }
    mediaRecorder.onstop = async () => {
      stream?.getTracks().forEach((t) => t.stop())
      const blob = new Blob(chunks, { type: mediaRecorder?.mimeType || mime || 'audio/webm' })
      await send(blob)
    }
    mediaRecorder.start()
    recording.value = true
  } catch (e) {
    stream?.getTracks().forEach((t) => t.stop())
    error.value = getErrorMessage(e, 'Unable to access microphone')
  }
}

function stopRecording() {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
  }
}

async function send(blob) {
  processing.value = true
  error.value = ''
  try {
    result.value = await submitShadow(blob, props.target)
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not score your recording')
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.shadow-exercise {
  background: rgba(var(--v-theme-secondary), 0.06);
  border: 1px solid rgba(var(--v-theme-secondary), 0.18);
}
</style>
