<template>
  <div class="spa-recorder speaking-runtime">
    <!-- Controlled response: typed answer -->
    <template v-if="isControlled">
      <v-textarea
        v-model="responseText"
        variant="outlined"
        rows="5"
        auto-grow
        class="mb-3"
        dir="ltr"
        :label="t('student.languages.speakingJourney.assessment.runtime.responseLabel')"
        :aria-label="t('student.languages.speakingJourney.assessment.runtime.responseLabel')"
        :disabled="disabled || submitting"
      />
    </template>

    <!-- Recorded response -->
    <template v-else>
      <div class="recorder-visual text-center py-4 px-3 mb-3 rounded-lg">
        <div class="timer-display mb-3" :class="{ active: recording }" aria-live="polite">
          <span class="timer-value" dir="ltr">{{ formattedTime }}</span>
          <span v-if="maxSeconds" class="timer-max text-caption text-medium-emphasis ms-2" dir="ltr">
            / {{ formatClock(maxSeconds) }}
          </span>
        </div>
        <div
          class="waveform d-flex justify-center align-end gap-1 mb-4"
          style="height: 48px"
          aria-hidden="true"
        >
          <div
            v-for="(h, i) in barHeights"
            :key="i"
            class="waveform-bar"
            :class="{ active: recording }"
            :style="{ height: `${h}px` }"
          />
        </div>
        <v-btn
          :color="recording ? 'error' : 'primary'"
          class="em-btn spk-pressable mb-2"
          :prepend-icon="recording ? 'mdi-stop' : 'mdi-microphone'"
          :disabled="disabled || submitting"
          :aria-label="
            recording
              ? t('student.languages.speakingJourney.assessment.runtime.stopRecording')
              : t('student.languages.speakingJourney.assessment.runtime.startRecording')
          "
          @click="onToggle"
        >
          {{
            recording
              ? t('student.languages.speakingJourney.assessment.runtime.stopRecording')
              : t('student.languages.speakingJourney.assessment.runtime.startRecording')
          }}
        </v-btn>
        <div v-if="micError" class="text-caption text-error mt-2" role="alert">{{ micError }}</div>
      </div>

      <audio
        v-if="playbackUrl"
        :src="playbackUrl"
        controls
        class="w-100 mb-3"
        :aria-label="t('student.languages.speakingJourney.assessment.runtime.playback')"
      />

      <v-textarea
        v-model="responseText"
        variant="outlined"
        rows="3"
        auto-grow
        class="mb-3"
        dir="ltr"
        :label="t('student.languages.speakingJourney.assessment.runtime.transcriptLabel')"
        :hint="t('student.languages.speakingJourney.assessment.runtime.transcriptHint')"
        persistent-hint
        :disabled="disabled || submitting || recording"
      />
    </template>

    <div class="d-flex flex-wrap gap-2">
      <v-btn
        color="primary"
        class="em-btn em-btn--primary spk-pressable"
        prepend-icon="mdi-send"
        :loading="submitting"
        :disabled="!canSubmit || disabled || recording"
        :aria-label="t('student.languages.speakingJourney.assessment.runtime.submitTask')"
        @click="onSubmit"
      >
        {{ t('student.languages.speakingJourney.assessment.runtime.submitTask') }}
      </v-btn>
      <v-btn
        v-if="!isControlled && (audioBlob || responseText)"
        variant="tonal"
        class="spk-pressable"
        :disabled="submitting || recording"
        @click="onReset"
      >
        {{ t('student.languages.speakingJourney.assessment.runtime.reRecord') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useVoiceRecorder } from '../../composables/useVoiceRecorder.js'

const props = defineProps({
  executionMode: { type: String, default: 'recorded_response' },
  minSeconds: { type: Number, default: 3 },
  maxSeconds: { type: Number, default: 90 },
  prepSeconds: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  resetKey: { type: [String, Number], default: '' },
})

const emit = defineEmits(['submit'])

const { t } = useI18n()
const isControlled = computed(() => props.executionMode === 'controlled_response')
const responseText = ref('')
const micError = ref('')
const playbackUrl = ref('')

const {
  recording,
  audioBlob,
  barHeights,
  formattedTime,
  toggleRecording,
  reset,
} = useVoiceRecorder({
  minSeconds: props.minSeconds,
  maxSeconds: props.maxSeconds || null,
})

const canSubmit = computed(() => {
  const text = responseText.value.trim()
  if (isControlled.value) return text.length > 0
  // Require a recording plus the student-confirmed transcript (backend evaluates transcript).
  return text.length > 0 && !!audioBlob.value
})

watch(
  () => props.resetKey,
  () => {
    onReset()
  },
)

watch(audioBlob, (blob) => {
  if (playbackUrl.value) URL.revokeObjectURL(playbackUrl.value)
  playbackUrl.value = blob ? URL.createObjectURL(blob) : ''
})

onUnmounted(() => {
  if (playbackUrl.value) URL.revokeObjectURL(playbackUrl.value)
})

function formatClock(total) {
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

async function onToggle() {
  micError.value = ''
  try {
    await toggleRecording()
  } catch {
    micError.value = t('student.languages.speakingJourney.assessment.runtime.micError')
  }
}

function onReset() {
  reset()
  responseText.value = ''
  micError.value = ''
  if (playbackUrl.value) {
    URL.revokeObjectURL(playbackUrl.value)
    playbackUrl.value = ''
  }
}

function onSubmit() {
  if (!canSubmit.value) return
  emit('submit', {
    transcriptText: responseText.value.trim(),
    mediaObjectId: null,
  })
}
</script>

<style scoped>
.recorder-visual {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.timer-value {
  font-size: 1.75rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.timer-display.active .timer-value {
  color: rgb(var(--v-theme-error));
}
.waveform-bar {
  width: 4px;
  border-radius: 2px;
  background: rgba(var(--v-theme-primary), 0.35);
  transition: height 0.09s linear;
}
.waveform-bar.active {
  background: rgb(var(--v-theme-primary));
}
</style>
