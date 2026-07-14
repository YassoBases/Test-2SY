<template>
  <div v-if="uploadOnly" class="voice-upload-only tds-scope">
    <button
      type="button"
      class="voice-upload-only__card"
      :disabled="uploading || isProcessing"
      @click="fileInput?.click()"
    >
      <span class="voice-upload-only__icon" aria-hidden="true">
        <v-icon icon="mdi-upload" size="28" />
      </span>
      <span class="voice-upload-only__label">{{ $t('teacher.actions.uploadVoiceSample') }}</span>
      <span class="voice-upload-only__hint">{{ $t('teacher.voice.uploadHint') }}</span>
    </button>
    <input
      ref="fileInput"
      type="file"
      accept="audio/*"
      class="d-none"
      @change="onFilePicked"
    />
    <v-progress-linear
      v-if="uploading || isProcessing"
      indeterminate
      height="4"
      rounded
      class="voice-upload-only__progress mt-3"
      color="primary"
    />
  </div>

  <v-card v-else class="glass-card glass-card--elevated pa-6 pa-md-8" variant="flat">
    <div class="d-flex align-center gap-3 mb-4 flex-wrap">
      <v-avatar size="48" class="eduspark-gradient" rounded="lg">
        <v-icon color="white">mdi-waveform</v-icon>
      </v-avatar>
      <div class="flex-grow-1">
        <span class="section-eyebrow mb-0">{{ $t('teacher.voice.eyebrow') }}</span>
        <div class="text-h6 font-weight-bold">{{ $t('teacher.voice.aiOnly') }}</div>
        <div class="text-caption text-medium-emphasis">
          {{ $t('teacher.voice.recordMinTemplate', { seconds: minSeconds }) }}
        </div>
      </div>
    </div>

    <v-alert
      v-if="sampleStatus?.status_label"
      :type="statusAlertType"
      variant="tonal"
      density="comfortable"
      class="mb-4 rounded-lg"
    >
      <div class="font-weight-medium">{{ sampleStatus.status_label }}</div>
      <div v-if="sampleStatus.duration_seconds" class="text-caption mt-1">
        {{ $t('teacher.labels.duration') }} {{ Math.round(sampleStatus.duration_seconds) }} {{ $t('teacher.voice.secondsShort') }} ·
        {{ formatUploadedAt(sampleStatus.uploaded_at) }}
      </div>
      <div v-if="sampleStatus.error_message" class="text-caption mt-1">{{ sampleStatus.error_message }}</div>
    </v-alert>

    <div class="recorder-visual text-center py-8 px-4">
      <div class="timer-display mb-6" :class="{ 'timer-display--active': recording }">
        <span class="timer-value">{{ formattedTime }}</span>
        <span class="timer-max">{{ $t('teacher.voice.minSecondsLabel', { seconds: minSeconds }) }}</span>
        <span v-if="recording && !meetsMinimum" class="timer-remaining">
          {{ $t('teacher.voice.remainingSeconds', { seconds: remainingSeconds }) }}
        </span>
        <span v-else-if="recording && meetsMinimum" class="timer-remaining text-success">
          {{ $t('teacher.voice.canStop') }}
        </span>
      </div>

      <div class="waveform d-flex justify-center align-end gap-1 mb-8" style="height: 64px">
        <div
          v-for="(h, i) in barHeights"
          :key="i"
          class="waveform-bar"
          :class="{ 'waveform-bar--active': recording }"
          :style="{ height: `${h}px`, animationDelay: recording ? `${i * 0.05}s` : '0s' }"
        />
      </div>

      <button
        type="button"
        class="mic-glow mx-auto d-block"
        :class="{ 'mic-glow--recording': recording }"
        :disabled="uploading || isProcessing"
        @click="toggleRecording"
      >
        <v-icon color="white" size="44">{{ recording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
      </button>

      <p class="recorder-status mt-6 mb-4" :class="statusClass">{{ statusText }}</p>

    <div class="d-flex flex-wrap justify-center gap-2">
      <v-btn
        variant="tonal"
        prepend-icon="mdi-upload"
        :disabled="recording || uploading || isProcessing"
        @click="fileInput?.click()"
      >
        {{ $t('teacher.actions.uploadAudio') }}
      </v-btn>
      <input
        ref="fileInput"
        type="file"
        accept="audio/*"
        class="d-none"
        @change="onFilePicked"
      />
      <v-btn
        v-if="ready && audioBlob && !sampleStatus?.ready && !deferUpload"
        color="primary"
        class="btn-glow"
        :loading="uploading"
        :disabled="!meetsMinimum || isProcessing"
        @click="emitUpload"
      >
        {{ $t('teacher.actions.uploadForProcessing') }}
      </v-btn>
    </div>

    <div v-if="audioBlob && previewUrl" class="audio-preview-box mt-5 pa-4 rounded-lg">
      <p class="text-caption text-medium-emphasis mb-2">{{ $t('teacher.voice.previewBeforeUpload') }}</p>
      <audio :src="previewUrl" controls class="w-100 mb-3" />
      <div class="d-flex flex-wrap gap-2">
        <v-btn size="small" variant="tonal" prepend-icon="mdi-refresh" :disabled="recording || uploading" @click="replaceRecording">
          {{ $t('teacher.actions.rerecord') }}
        </v-btn>
        <v-btn size="small" variant="tonal" color="error" prepend-icon="mdi-delete" :disabled="recording || uploading" @click="deleteRecording">
          {{ $t('teacher.actions.deleteRecording') }}
        </v-btn>
      </div>
    </div>
    </div>

    <v-progress-linear
      :model-value="progressPercent"
      height="6"
      rounded
      class="progress-glow mb-2"
      :color="recording ? 'error' : sampleStatus?.ready ? 'success' : 'primary'"
    />
  </v-card>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useVoiceRecorder } from '../../composables/useVoiceRecorder.js'
import { VOICE_SAMPLE_MIN_SECONDS } from '../../constants/app.js'

const props = defineProps({
  minSeconds: { type: Number, default: VOICE_SAMPLE_MIN_SECONDS },
  sampleStatus: { type: Object, default: null },
  uploading: { type: Boolean, default: false },
  deferUpload: { type: Boolean, default: false },
  uploadOnly: { type: Boolean, default: false },
})

const emit = defineEmits(['update:ready', 'update:audioBlob', 'upload', 'deleted'])

const fileInput = ref(null)
const previewUrl = ref('')

const {
  recording,
  ready,
  audioBlob,
  barHeights,
  formattedTime,
  progressPercent,
  remainingSeconds,
  meetsMinimum,
  toggleRecording,
  setBlob,
  reset,
} = useVoiceRecorder({ minSeconds: props.minSeconds })

const isProcessing = computed(() =>
  ['pending', 'processing'].includes(props.sampleStatus?.processing_status),
)

const statusAlertType = computed(() => {
  const s = props.sampleStatus?.processing_status
  if (s === 'ready') return 'success'
  if (s === 'failed') return 'error'
  if (s === 'pending' || s === 'processing') return 'info'
  return 'info'
})

const statusText = computed(() => {
  if (props.uploading) return t('teacher.status.uploadingSample')
  if (isProcessing.value) return t('teacher.status.processingVoice')
  if (props.sampleStatus?.ready) return t('teacher.status.voiceReady')
  if (props.sampleStatus?.processing_status === 'failed') return t('teacher.voice.analysisFailed')
  if (recording.value) return t('teacher.status.recording')
  if (ready.value && !meetsMinimum.value) return t('teacher.voice.recordMinStatusTemplate', { seconds: props.minSeconds })
  if (ready.value && props.deferUpload) return t('teacher.voice.deferUploadHint')
  if (ready.value) return t('teacher.voice.uploadOrFileHint')
  return t('teacher.voice.micOrFileHint')
})

const statusClass = computed(() => ({
  'recorder-status--active': recording.value,
  'recorder-status--done': props.sampleStatus?.ready,
}))

function formatUploadedAt(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('ar-SY')
  } catch {
    return iso
  }
}

function emitUpload() {
  if (audioBlob.value) emit('upload', audioBlob.value)
}

function onFilePicked(e) {
  const file = e.target.files?.[0]
  if (file) {
    setBlob(file)
    if (!props.deferUpload) emit('upload', file)
  }
  e.target.value = ''
}

function replaceRecording() {
  reset()
  emit('deleted')
}

function deleteRecording() {
  reset()
  emit('deleted')
}

watch(audioBlob, (blob) => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = blob ? URL.createObjectURL(blob) : ''
  emit('update:audioBlob', blob)
}, { immediate: true })

watch(
  () => props.sampleStatus?.ready,
  (val) => emit('update:ready', !!val),
  { immediate: true },
)

onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<style scoped>
.recorder-visual {
  background:
    radial-gradient(ellipse 80% 60% at 50% 100%, rgba(124, 108, 240, 0.18) 0%, transparent 60%),
    rgba(8, 12, 24, 0.5);
  border-radius: 20px;
  border: 1px solid rgba(124, 108, 240, 0.15);
}

.timer-value {
  font-family: 'Cairo', monospace;
  font-size: clamp(2.5rem, 6vw, 3.25rem);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  background: linear-gradient(135deg, #e8ecf4 0%, #22d3ee 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.timer-display--active .timer-value {
  background: linear-gradient(135deg, #fca5a5 0%, #f87171 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.timer-max {
  display: block;
  font-size: 0.85rem;
  color: var(--em-text-muted);
  margin-top: 4px;
}

.timer-remaining {
  display: block;
  font-size: 0.75rem;
  color: var(--em-cyan);
  margin-top: 8px;
}

.recorder-status {
  color: var(--em-text-muted);
  font-size: 0.95rem;
}

.recorder-status--active {
  color: #f87171;
}

.recorder-status--done {
  color: #34d399;
}

.audio-preview-box {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-border-color), 0.12);
}

.voice-upload-only__card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--em-space-sm);
  width: 100%;
  padding: var(--em-space-xl) var(--em-space-lg);
  border-radius: var(--em-radius-lg, 16px);
  border: 1px dashed color-mix(in srgb, var(--em-primary) 35%, var(--em-border-subtle));
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.03));
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.voice-upload-only__card:hover:not(:disabled) {
  border-color: var(--em-primary);
  background: color-mix(in srgb, var(--em-primary) 6%, transparent);
}

.voice-upload-only__card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.voice-upload-only__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--em-primary) 14%, transparent);
  color: var(--em-primary-deep, var(--em-primary));
}

.voice-upload-only__label {
  font-size: 1rem;
  font-weight: 700;
  color: var(--em-text);
}

.voice-upload-only__hint {
  font-size: 0.8125rem;
  color: var(--em-text-muted);
  text-align: center;
  max-width: 22rem;
}

.voice-upload-only__progress {
  width: 100%;
}
</style>
