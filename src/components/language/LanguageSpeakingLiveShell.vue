<template>
  <div class="speaking-live-shell speaking-runtime">
    <!-- Intro only in true pre-session states (never mid-session error). -->
    <v-card v-if="showHero" class="glass-card pa-6 mb-4 speaking-live-hero" variant="flat" tabindex="-1" data-spk-focus="alex">
      <div class="d-flex align-start gap-4 flex-wrap">
        <v-avatar color="secondary" size="72" class="alex-avatar flex-shrink-0">
          <v-icon size="36" aria-hidden="true">mdi-account-voice</v-icon>
        </v-avatar>
        <div class="flex-grow-1">
          <div class="text-h5 mb-2">{{ t('student.languages.speaking.live.heroTitle') }}</div>
          <p class="text-body-1 mb-2">{{ t('student.languages.speaking.live.heroLead') }}</p>
          <ul class="hero-points text-body-2 mb-3">
            <li>{{ t('student.languages.speaking.live.heroPoint1') }}</li>
            <li>{{ t('student.languages.speaking.live.heroPoint2') }}</li>
            <li>{{ t('student.languages.speaking.live.heroPoint3') }}</li>
          </ul>
          <p class="text-body-2 text-medium-emphasis mb-4">{{ t('student.languages.speaking.live.micExplain') }}</p>
          <p
            v-if="remainingSeconds != null"
            class="text-body-2 mb-4"
            data-testid="alex-daily-remaining"
          >
            {{ t('student.languages.speaking.live.timeRemaining', { seconds: remainingSeconds }) }}
          </p>
          <v-btn
            color="secondary"
            size="large"
            class="em-btn em-btn--secondary spk-pressable"
            :disabled="!canPrimaryStart"
            :loading="false"
            :aria-label="t('student.languages.speaking.live.startSpeaking')"
            @click="onPrimaryAction"
          >
            {{ t('student.languages.speaking.live.startSpeaking') }}
          </v-btn>
          <p v-if="requirePreparedSession && !journeyLiveSessionId" class="text-caption text-medium-emphasis mt-3 mb-0">
            {{ t('student.languages.speakingJourney.alex.needSession') }}
          </p>
        </div>
      </div>
    </v-card>

    <!-- Live surface: starting / active / ending / error -->
    <v-card v-if="showLiveSurface" class="glass-card pa-5 speaking-live-stage" variant="flat">
      <div
        class="live-status-banner mb-4"
        role="status"
        aria-live="polite"
        :aria-label="statusText"
      >
        <div class="d-flex align-center gap-3 flex-wrap">
          <div
            class="alex-state-indicator"
            :class="[`state-${visualState}`, { reduced: prefersReducedMotion, muted: micMuted }]"
            aria-hidden="true"
          >
            <span class="pulse-ring" />
            <v-icon size="28">{{ visualState === 'listening' ? 'mdi-microphone' : 'mdi-account-voice' }}</v-icon>
          </div>
          <div class="flex-grow-1 min-width-0">
            <div class="text-subtitle-1 font-weight-medium">{{ statusText }}</div>
            <div v-if="processingTurn" class="text-caption text-medium-emphasis">
              {{ t('student.languages.speaking.live.processingHint') }}
            </div>
            <div v-else-if="micMuted" class="text-caption text-medium-emphasis">
              {{ t('student.languages.speaking.live.micMutedHint') }}
            </div>
            <div v-else-if="isListening && !currentStudentUtterance" class="text-caption text-medium-emphasis">
              {{ t('student.languages.speaking.live.listeningHint') }}
            </div>
            <div
              v-if="remainingSeconds != null && state !== 'error'"
              class="text-caption text-medium-emphasis mt-1"
              data-testid="alex-session-remaining"
            >
              {{ t('student.languages.speaking.live.timeRemaining', { seconds: remainingSeconds }) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Active student utterance (interim when available, else Listening). -->
      <v-card
        v-if="isListening || currentStudentUtterance"
        class="live-student-bubble pa-3 mb-4"
        variant="tonal"
        color="success"
      >
        <div class="text-caption font-weight-medium mb-1">
          {{ t('student.languages.speaking.live.youLabel') }}
          <span class="text-medium-emphasis">
            · {{ currentStudentUtterance ? t('student.languages.speaking.live.speakingNow') : t('student.languages.speaking.live.listeningLabel') }}
          </span>
        </div>
        <div v-if="currentStudentUtterance" class="text-body-2" dir="ltr">{{ currentStudentUtterance }}</div>
        <div v-else class="text-body-2 text-medium-emphasis">
          {{ t('student.languages.speaking.live.listeningHint') }}
        </div>
      </v-card>

      <v-alert
        v-if="personalizationFailed"
        type="info"
        variant="tonal"
        density="comfortable"
        class="mb-4"
      >
        {{ t('student.languages.speaking.live.personalizationLimited') }}
      </v-alert>

      <v-alert v-if="displayError" type="warning" variant="tonal" class="mb-4" role="alert">
        {{ displayError }}
        <template v-if="state === 'error'" #append>
          <v-btn
            variant="text"
            size="small"
            class="spk-pressable"
            :aria-label="t('student.languages.speaking.live.retry')"
            @click="onRetry"
          >
            {{ t('student.languages.speaking.live.retry') }}
          </v-btn>
        </template>
      </v-alert>

      <div class="live-controls d-flex gap-2 flex-wrap mb-4">
        <v-btn
          variant="tonal"
          :color="micMuted ? 'warning' : 'success'"
          :disabled="!micGranted || state === 'error' || state === 'ending'"
          :prepend-icon="micMuted ? 'mdi-microphone-off' : 'mdi-microphone'"
          :aria-label="micMuted ? t('student.languages.speaking.live.unmute') : t('student.languages.speaking.live.mute')"
          @click="toggleMute"
        >
          {{ micMuted ? t('student.languages.speaking.live.unmute') : t('student.languages.speaking.live.mute') }}
        </v-btn>
        <v-btn
          v-if="state !== 'error'"
          color="error"
          variant="tonal"
          :loading="state === 'ending'"
          :aria-label="t('student.languages.speaking.live.endConversation')"
          @click="onEnd"
        >
          {{ t('student.languages.speaking.live.endConversation') }}
        </v-btn>
        <v-btn
          v-else
          color="secondary"
          variant="flat"
          :aria-label="t('student.languages.speaking.live.retry')"
          @click="onRetry"
        >
          {{ t('student.languages.speaking.live.retry') }}
        </v-btn>
      </div>

      <v-expansion-panels v-if="transcriptMessages.length" variant="accordion" class="transcript-panel">
        <v-expansion-panel>
          <v-expansion-panel-title>{{ t('student.languages.speaking.live.transcriptTitle') }}</v-expansion-panel-title>
          <v-expansion-panel-text>
            <div
              v-for="msg in transcriptMessages"
              :key="msg.id"
              class="transcript-line mb-2"
              :class="msg.role === 'alex' ? 'from-alex' : 'from-student'"
            >
              <span class="text-caption font-weight-medium d-block mb-1">
                {{ msg.role === 'alex' ? t('student.languages.speaking.live.alexLabel') : t('student.languages.speaking.live.youLabel') }}
              </span>
              <span class="text-body-2" dir="ltr">{{ msg.text }}</span>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card>

    <LanguageSpeakingSessionSummary
      v-if="state === 'ended'"
      class="mt-4"
      :summaries="turnSummaries"
      :show-all="turnSummaries.length > 1"
    />

    <div v-if="state === 'ended'" class="d-flex gap-2 mt-4 flex-wrap">
      <v-btn
        v-if="canPrimaryStart"
        color="secondary"
        class="em-btn em-btn--secondary spk-pressable"
        :aria-label="t('student.languages.speaking.live.startSpeaking')"
        @click="onStartFresh"
      >
        {{ t('student.languages.speaking.live.startSpeaking') }}
      </v-btn>
      <v-btn
        variant="tonal"
        class="spk-pressable"
        prepend-icon="mdi-arrow-left"
        :aria-label="t('student.languages.speakingJourney.alex.backToLesson')"
        @click="$emit('back-to-lesson')"
      >
        {{ t('student.languages.speakingJourney.alex.backToLesson') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLiveConversation } from '../../composables/useLiveConversation.js'
import LanguageSpeakingSessionSummary from './LanguageSpeakingSessionSummary.vue'

const props = defineProps({
  initialTaskPrompt: { type: String, default: '' },
  journeyLiveSessionId: { type: String, default: '' },
  /** When true, refuse to start live without a prepared journey live_session_id. */
  requirePreparedSession: { type: Boolean, default: false },
})

const emit = defineEmits(['session-ended', 'back-to-lesson'])

const { t } = useI18n()
const prefersReducedMotion = ref(false)

const {
  state,
  errorMessage,
  canStart,
  showLiveSurface,
  processingTurn,
  personalizationFailed,
  transcriptMessages,
  currentStudentUtterance,
  turnSummaries,
  micGranted,
  micMuted,
  isListening,
  remainingSeconds,
  startLiveSession,
  endLiveSession,
  retryAfterError,
  toggleMute,
} = useLiveConversation()

const showHero = computed(() => state.value === 'idle' || state.value === 'ended')

const canPrimaryStart = computed(() => {
  if (props.requirePreparedSession && !props.journeyLiveSessionId) return false
  return canStart.value
})

/** Prefer student-safe i18n over raw reconnect / internal phrases. */
const displayError = computed(() => {
  const raw = String(errorMessage.value || '').trim()
  if (!raw) return ''
  const lower = raw.toLowerCase()
  if (/connection lost|reconnect/i.test(lower)) {
    return t('student.languages.speaking.live.errors.reconnect')
  }
  if (/microphone|mic/i.test(lower)) {
    return t('student.languages.speaking.live.errors.mic')
  }
  if (/budget|time remaining|daily/i.test(lower)) {
    return t('student.languages.speaking.live.errors.budget')
  }
  if (/unavailable|not ready|context/i.test(lower)) {
    return t('student.languages.speaking.live.errors.unavailable')
  }
  if (/expired|lease/i.test(lower)) {
    return t('student.languages.speaking.live.errors.expired')
  }
  if (/traceback|sqlalchemy|websocket|localhost/i.test(lower)) {
    return t('student.languages.speaking.live.errors.generic')
  }
  return raw
})

const visualState = computed(() => {
  if (processingTurn.value) return 'processing'
  if (state.value === 'alex_speaking') return 'alex'
  if (state.value === 'student_speaking' || state.value === 'ready') return 'listening'
  if (state.value === 'connecting' || state.value === 'requesting_microphone' || state.value === 'reconnecting') {
    return 'connecting'
  }
  if (state.value === 'error') return 'idle'
  return 'idle'
})

const statusText = computed(() => {
  const key = `student.languages.speaking.live.states.${state.value}`
  const translated = t(key)
  if (translated !== key) return translated
  return t('student.languages.speaking.live.states.ready')
})

let motionQuery
function syncReducedMotion() {
  prefersReducedMotion.value = motionQuery?.matches ?? false
}

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  syncReducedMotion()
  motionQuery.addEventListener?.('change', syncReducedMotion)
  if (props.journeyLiveSessionId) {
    void startLiveSession({
      taskPrompt: props.initialTaskPrompt || t('student.languages.speaking.live.defaultPrompt'),
      liveSessionId: props.journeyLiveSessionId,
    })
  }
})

watch(
  () => props.journeyLiveSessionId,
  (id) => {
    if (id && canStart.value) {
      void startLiveSession({
        taskPrompt: props.initialTaskPrompt || t('student.languages.speaking.live.defaultPrompt'),
        liveSessionId: id,
      })
    }
  },
)

onUnmounted(() => {
  motionQuery?.removeEventListener?.('change', syncReducedMotion)
})

async function onPrimaryAction() {
  if (!canPrimaryStart.value) return
  await startLiveSession({
    taskPrompt: props.initialTaskPrompt || t('student.languages.speaking.live.defaultPrompt'),
    liveSessionId: props.journeyLiveSessionId || undefined,
  })
}

async function onStartFresh() {
  if (!canPrimaryStart.value) return
  await startLiveSession({
    taskPrompt: props.initialTaskPrompt || t('student.languages.speaking.live.defaultPrompt'),
    liveSessionId: props.journeyLiveSessionId || undefined,
  })
}

async function onEnd() {
  await endLiveSession({ finalizePendingTurn: true })
  emit('session-ended')
}

async function onRetry() {
  await retryAfterError()
}
</script>

<style scoped>
.speaking-live-shell {
  max-width: 760px;
}
.hero-points {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.speaking-live-stage {
  min-height: 280px;
}
.live-controls {
  position: sticky;
  bottom: calc(env(safe-area-inset-bottom, 0px) + 12px);
  z-index: 2;
  background: rgba(var(--v-theme-surface), 0.92);
  padding-top: 0.5rem;
}
.live-student-bubble {
  border-radius: 14px;
}
.alex-state-indicator {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-secondary), 0.12);
  flex-shrink: 0;
}
.alex-state-indicator .pulse-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(var(--v-theme-secondary), 0.35);
  animation: alex-pulse 1.8s ease-out infinite;
}
.alex-state-indicator.reduced .pulse-ring,
.alex-state-indicator.muted .pulse-ring {
  animation: none;
  opacity: 0.35;
}
.alex-state-indicator.state-alex .pulse-ring {
  animation-duration: 1.2s;
}
.alex-state-indicator.state-listening .pulse-ring {
  border-color: rgba(var(--v-theme-success), 0.45);
}
.alex-state-indicator.state-processing .pulse-ring {
  animation-duration: 2.4s;
}
.min-width-0 {
  min-width: 0;
}
@keyframes alex-pulse {
  0% { transform: scale(0.92); opacity: 0.9; }
  70% { transform: scale(1.15); opacity: 0.15; }
  100% { transform: scale(1.2); opacity: 0; }
}
.transcript-line.from-alex {
  border-inline-start: 3px solid rgba(var(--v-theme-info), 0.5);
  padding-inline-start: 0.75rem;
}
.transcript-line.from-student {
  border-inline-start: 3px solid rgba(var(--v-theme-success), 0.5);
  padding-inline-start: 0.75rem;
}
@media (max-width: 600px) {
  .speaking-live-shell {
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }
  .speaking-live-stage {
    min-height: 240px;
  }
}
</style>
