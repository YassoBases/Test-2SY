<template>
  <div class="wa-composer-root">
    <v-alert
      v-if="localError"
      type="warning"
      variant="tonal"
      density="compact"
      class="mb-2 rounded-lg"
      closable
      @click:close="localError = ''"
    >
      {{ localError }}
    </v-alert>

    <div v-if="voicePhase === 'recording'" class="wa-voice-bar wa-voice-bar--recording">
      <v-btn size="small" variant="text" color="error" @click="cancelRecording">{{ t('messages.composer.cancel') }}</v-btn>
      <span class="wa-voice-bar__timer" aria-live="polite">{{ recordElapsedLabel }}</span>
      <v-spacer />
      <v-btn size="small" color="error" variant="flat" prepend-icon="mdi-stop" @click="stopRecording">
        {{ t('messages.composer.stop') }}
      </v-btn>
    </div>

    <div v-else-if="voicePhase === 'stopped' && pendingPreview?.type === 'voice'" class="wa-voice-bar wa-voice-bar--stopped">
      <audio ref="previewAudioEl" :src="pendingPreview.url" class="wa-voice-bar__audio" preload="metadata" />
      <div class="d-flex align-center gap-2 flex-wrap w-100">
        <v-btn size="small" variant="text" color="error" prepend-icon="mdi-delete-outline" @click="deleteVoiceRecording">
          {{ t('messages.composer.delete') }}
        </v-btn>
        <v-btn size="small" variant="tonal" prepend-icon="mdi-play-circle-outline" @click="playVoicePreview">
          {{ t('messages.composer.preview') }}
        </v-btn>
        <v-spacer />
        <v-btn size="small" color="primary" variant="flat" prepend-icon="mdi-send" :loading="sending" @click="sendPending">
          {{ t('messages.composer.send') }}
        </v-btn>
      </div>
    </div>

    <div v-else-if="pendingPreview && pendingPreview.type !== 'voice'" class="wa-composer-preview">
      <div class="d-flex justify-space-between align-center mb-2">
        <span class="text-caption font-weight-bold">{{ t('messages.composer.preview') }}</span>
        <v-btn icon size="x-small" variant="text" @click="clearPending"><v-icon>mdi-close</v-icon></v-btn>
      </div>
      <img v-if="pendingPreview.type === 'image'" :src="pendingPreview.url" class="wa-composer-preview__img" alt="" />
      <div v-else class="text-body-2 d-flex align-center gap-2">
        <v-icon size="20">{{ pendingPreview.type === 'pdf' ? 'mdi-file-pdf-box' : 'mdi-file-outline' }}</v-icon>
        <span class="text-truncate">{{ pendingPreview.name }}</span>
      </div>
      <input
        v-model="pendingCaption"
        type="text"
        class="wa-composer-preview__caption mt-2"
        :placeholder="t('messages.composer.commentPlaceholder')"
      />
      <div class="d-flex justify-end gap-2 mt-2">
        <v-btn size="small" variant="text" @click="clearPending">{{ t('messages.composer.cancel') }}</v-btn>
        <v-btn size="small" color="primary" :loading="sending" @click="sendPending">{{ t('messages.composer.send') }}</v-btn>
      </div>
    </div>

    <div
      v-if="voicePhase !== 'recording' && !(voicePhase === 'stopped' && pendingPreview?.type === 'voice')"
      class="wa-composer"
      :class="{ 'wa-composer--focused': composerFocused }"
    >
      <div class="wa-composer__shell">
        <button
          type="button"
          class="wa-composer__icon-btn"
          :title="t('messages.composer.attachment')"
          :disabled="voicePhase === 'stopped'"
          @click="fileInput?.click()"
        >
          <v-icon size="20">mdi-paperclip</v-icon>
        </button>
        <input ref="fileInput" type="file" class="d-none" accept="image/*,.pdf,.doc,.docx,.txt" @change="onFilePick" />

        <textarea
          ref="textareaEl"
          v-model="draft"
          class="wa-composer__textarea"
          rows="1"
          :placeholder="t('messages.composer.messagePlaceholder')"
          :disabled="voicePhase === 'stopped'"
          @input="resizeTextarea"
          @keydown.enter.exact.prevent="onEnterSend"
          @focus="composerFocused = true"
          @blur="composerFocused = false"
        />

        <button
          type="button"
          class="wa-composer__icon-btn"
          :title="t('messages.composer.voiceMessage')"
          :disabled="voicePhase === 'stopped'"
          @click="startRecording"
        >
          <v-icon size="20">mdi-microphone</v-icon>
        </button>

        <button
          type="button"
          class="wa-composer__send"
          :class="{ 'wa-composer__send--active': canSend }"
          :disabled="!canSend || sending"
          :title="t('messages.composer.send')"
          @click="onSendClick"
        >
          <v-progress-circular v-if="sending" indeterminate size="18" width="2" color="white" />
          <v-icon v-else size="18">mdi-send</v-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  extensionForMime,
  getPreferredRecorderMime,
  validateVoiceBlob,
} from '../../utils/voiceRecording.js'
import { MAX_PDF_SIZE_BYTES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'

defineProps({
  sending: { type: Boolean, default: false },
})

const emit = defineEmits(['send-text', 'send-attachment', 'error'])

const { t } = useI18n()

/** idle | recording | stopped */
const voicePhase = ref('idle')
const composerFocused = ref(false)

const draft = ref('')
const textareaEl = ref(null)
const fileInput = ref(null)
const previewAudioEl = ref(null)
const pendingPreview = ref(null)
const pendingCaption = ref('')
const pendingFile = ref(null)
const localError = ref('')
const recordStartedAt = ref(0)
const recordElapsedMs = ref(0)

let mediaRecorder = null
let recordChunks = []
let recordTimer = null
let activeStream = null
let activeMime = ''

const canSend = computed(() => {
  if (voicePhase.value !== 'idle') return false
  return !!draft.value.trim()
})

const recordElapsedLabel = computed(() => {
  const s = Math.floor(recordElapsedMs.value / 1000)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
})

function setError(msg) {
  localError.value = msg
  emit('error', msg)
}

function resizeTextarea() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`
}

function releaseStream() {
  activeStream?.getTracks().forEach((track) => track.stop())
  activeStream = null
}

function stopRecordTimer() {
  if (recordTimer) {
    clearInterval(recordTimer)
    recordTimer = null
  }
}

function resetRecorder() {
  stopRecordTimer()
  releaseStream()
  mediaRecorder = null
  recordChunks = []
  recordElapsedMs.value = 0
  recordStartedAt.value = 0
  activeMime = ''
}

function clearPending() {
  if (pendingPreview.value?.url) URL.revokeObjectURL(pendingPreview.value.url)
  pendingPreview.value = null
  pendingCaption.value = ''
  pendingFile.value = null
}

function deleteVoiceRecording() {
  clearPending()
  resetRecorder()
  voicePhase.value = 'idle'
  localError.value = ''
}

function cancelRecording() {
  if (mediaRecorder?.state === 'recording') {
    mediaRecorder.onstop = null
    try {
      mediaRecorder.stop()
    } catch {
      /* ignore */
    }
  }
  resetRecorder()
  voicePhase.value = 'idle'
}

function onFilePick(ev) {
  const file = ev.target.files?.[0]
  ev.target.value = ''
  if (!file) return
  localError.value = ''
  const url = URL.createObjectURL(file)
  let type = 'file'
  if (file.type.startsWith('image/')) type = 'image'
  else if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
    type = 'pdf'
    if (file.size > MAX_PDF_SIZE_BYTES) {
      localError.value = t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL })
      return
    }
  }
  deleteVoiceRecording()
  pendingFile.value = file
  pendingPreview.value = { type, url, name: file.name }
}

function createMediaRecorder(stream, mime) {
  if (mime) {
    try {
      return new MediaRecorder(stream, { mimeType: mime })
    } catch {
      /* fall through */
    }
  }
  return new MediaRecorder(stream)
}

async function startRecording() {
  if (voicePhase.value === 'recording') return

  localError.value = ''
  activeMime = getPreferredRecorderMime()

  if (typeof MediaRecorder === 'undefined') {
    setError(t('messages.composer.recordingUnsupported'))
    return
  }

  try {
    activeStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    recordChunks = []
    mediaRecorder = createMediaRecorder(activeStream, activeMime)
    if (!activeMime && mediaRecorder.mimeType) activeMime = mediaRecorder.mimeType

    mediaRecorder.ondataavailable = (e) => {
      if (e.data?.size) recordChunks.push(e.data)
    }

    mediaRecorder.onerror = () => {
      setError(t('messages.composer.recordingFailed'))
      cancelRecording()
    }

    mediaRecorder.onstop = () => {
      stopRecordTimer()
      releaseStream()

      const durationMs = Date.now() - recordStartedAt.value
      const blobType = activeMime || mediaRecorder?.mimeType || 'audio/webm'
      const blob = new Blob(recordChunks, { type: blobType })
      const validationError = validateVoiceBlob(blob, durationMs)

      recordChunks = []
      mediaRecorder = null

      if (validationError) {
        voicePhase.value = 'idle'
        setError(validationError)
        return
      }

      const ext = extensionForMime(blobType)
      const file = new File([blob], `voice_${Date.now()}${ext}`, { type: blobType.split(';')[0] })
      clearPending()
      pendingFile.value = file
      pendingPreview.value = {
        type: 'voice',
        url: URL.createObjectURL(blob),
        name: file.name,
        durationMs,
      }
      voicePhase.value = 'stopped'
    }

    recordStartedAt.value = Date.now()
    recordElapsedMs.value = 0
    recordTimer = setInterval(() => {
      recordElapsedMs.value = Date.now() - recordStartedAt.value
    }, 200)

    mediaRecorder.start(250)
    voicePhase.value = 'recording'
  } catch {
    resetRecorder()
    voicePhase.value = 'idle'
    setError(t('messages.composer.micDenied'))
  }
}

function stopRecording() {
  if (voicePhase.value !== 'recording' || !mediaRecorder) return
  if (mediaRecorder.state === 'recording') {
    try {
      mediaRecorder.requestData()
    } catch {
      /* optional */
    }
    mediaRecorder.stop()
  }
}

function playVoicePreview() {
  const el = previewAudioEl.value
  if (!el) return
  el.currentTime = 0
  el.play().catch(() => setError(t('messages.composer.previewFailed')))
}

function sendPending() {
  if (!pendingFile.value) return
  if (pendingPreview.value?.type === 'voice') {
    const err = validateVoiceBlob(pendingFile.value, pendingPreview.value.durationMs)
    if (err) {
      setError(err)
      return
    }
  }
  localError.value = ''
  emit('send-attachment', {
    file: pendingFile.value,
    caption: pendingCaption.value,
    voiceDurationMs: pendingPreview.value?.durationMs ?? null,
  })
  clearPending()
  resetRecorder()
  voicePhase.value = 'idle'
}

function onSendClick() {
  if (pendingPreview.value) {
    sendPending()
    return
  }
  if (draft.value.trim()) emit('send-text', draft.value.trim())
}

function onEnterSend() {
  onSendClick()
}

defineExpose({
  clearDraft() {
    draft.value = ''
    deleteVoiceRecording()
    nextTick(resizeTextarea)
  },
  focusInput() {
    textareaEl.value?.focus()
  },
})

onMounted(() => resizeTextarea())

onUnmounted(() => {
  if (mediaRecorder?.state === 'recording') {
    try {
      mediaRecorder.stop()
    } catch {
      /* ignore */
    }
  }
  deleteVoiceRecording()
})
</script>

<style scoped>
.wa-voice-bar {
  padding: 10px 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.wa-voice-bar--recording {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(239, 68, 68, 0.12);
}

.wa-voice-bar--stopped {
  background: rgba(30, 41, 59, 0.6);
}

.wa-voice-bar__timer {
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  font-size: 1rem;
  color: #fca5a5;
  min-width: 48px;
  text-align: center;
}

.wa-voice-bar__audio {
  display: none;
}

.wa-composer-preview__caption {
  width: 100%;
  border: none;
  outline: none;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 8px 10px;
  color: inherit;
  font-size: 0.85rem;
}
</style>
