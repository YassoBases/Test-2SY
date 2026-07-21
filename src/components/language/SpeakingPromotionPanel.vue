<template>
  <div class="speaking-promotion speaking-runtime">
    <!-- Completing intermediate -->
    <v-card
      v-if="phase === 'completing'"
      class="glass-card pa-6 mb-4"
      variant="flat"
      role="status"
      aria-live="polite"
    >
      <div class="text-overline text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
      </div>
      <h2 class="text-h5 font-weight-bold mb-2">
        {{ t('student.languages.speakingJourney.assessment.completing.title') }}
      </h2>
      <p class="text-body-2 text-medium-emphasis mb-4">
        {{ t('student.languages.speakingJourney.assessment.completing.body') }}
      </p>
      <LoadingState variant="cards" :count="1" class="spk-skeleton-block" />
    </v-card>

    <SpeakingPromotionIntro
      v-else-if="phase === 'intro'"
      :source-cefr="sourceCefr"
      :target-cefr="targetCefr"
      :estimated-duration-seconds="estimatedDurationSeconds"
      :task-count="taskCount"
      :has-interaction-gaps="hasInteractionGaps"
      :loading="sessionLoading"
      :session-error="sessionError"
      @begin="$emit('begin-tasks')"
      @back="$emit('back-home')"
    />

    <SpeakingPromotionRuntime
      v-else-if="phase === 'runtime'"
      :current-task="currentTask"
      :task-count="taskCount"
      :completed-task-count="completedTaskCount"
      :remaining-task-count="remainingTaskCount"
      :submit-loading="submitLoading"
      :action-loading="actionLoading"
      :session-error="sessionError"
      :submit-error="submitError"
      :last-submit="lastSubmit"
      @submit-task="$emit('submit-task', $event)"
      @abandon="$emit('abandon')"
      @reconnect="$emit('resume')"
    />

    <SpeakingPromotionResult
      v-else-if="phase === 'result'"
      :result="result"
      :result-loading="resultLoading"
      :result-error="resultError"
      :session-error="sessionError"
      :session-loading="sessionLoading"
      :can-retry="canRetry"
      :can-promote="canPromote"
      :promote-loading="promoteLoading"
      :promote-error="promoteError"
      :promotion-result="promotionResult"
      :official-promoted="officialPromoted"
      @retry="$emit('retry')"
      @retry-load="$emit('view-result')"
      @back-to-journey="$emit('back-to-journey')"
      @back-home="$emit('back-home')"
      @promote="$emit('promote')"
    />

    <!-- Assessment Home -->
    <template v-else>
      <v-alert v-if="statusError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        <div class="d-flex flex-wrap align-center justify-space-between gap-2">
          <span>{{ statusError }}</span>
          <v-btn
            size="small"
            variant="text"
            class="spk-pressable"
            :loading="statusLoading"
            :aria-label="t('student.languages.speakingJourney.runtime.retry')"
            @click="$emit('retry-status')"
          >
            {{ t('student.languages.speakingJourney.runtime.retry') }}
          </v-btn>
        </div>
      </v-alert>
      <v-alert v-if="assessmentError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        {{ assessmentError }}
      </v-alert>
      <v-alert v-if="sessionError && homeState !== 'error'" type="warning" variant="tonal" class="mb-4 rounded-lg" role="alert">
        {{ sessionError }}
      </v-alert>

      <LoadingState v-if="homeState === 'loading'" variant="cards" :count="2" class="spk-skeleton-block" />

      <v-card v-else class="glass-card pa-6 mb-6" variant="flat">
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
        </div>
        <h2 class="text-h5 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.assessment.title') }}
        </h2>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ message || t('student.languages.speakingJourney.assessment.defaultMessage') }}
        </p>

        <v-chip
          size="small"
          class="mb-4"
          :color="stateChipColor"
          variant="tonal"
        >
          {{ stateLabel }}
        </v-chip>

        <v-row dense class="mb-4">
          <v-col cols="6" sm="3">
            <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.source') }}</div>
            <div class="stat-value" dir="ltr">{{ sourceCefr || '—' }}</div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.target') }}</div>
            <div class="stat-value" dir="ltr">{{ targetCefr || '—' }}</div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.duration') }}</div>
            <div class="stat-value">
              {{
                estimatedDurationSeconds
                  ? t('student.languages.speakingJourney.assessment.durationValue', {
                      minutes: Math.ceil(estimatedDurationSeconds / 60),
                    })
                  : '—'
              }}
            </div>
          </v-col>
          <v-col cols="6" sm="3">
            <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.intro.tasks') }}</div>
            <div class="stat-value">
              {{ taskCount ? t('student.languages.speakingJourney.assessment.taskCount', { n: taskCount }) : '—' }}
            </div>
          </v-col>
        </v-row>

        <v-alert
          v-if="homeState === 'locked'"
          type="warning"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-lock-outline"
        >
          <div class="text-body-2 font-weight-medium mb-1">
            {{ t('student.languages.speakingJourney.assessment.whyLockedTitle') }}
          </div>
          <div class="text-body-2">
            {{ message || t('student.languages.speakingJourney.assessment.whyLockedBody') }}
          </div>
        </v-alert>
        <v-alert
          v-else-if="homeState === 'in_progress'"
          type="info"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-play-circle-outline"
        >
          {{ t('student.languages.speakingJourney.assessment.home.inProgressBody') }}
        </v-alert>
        <v-alert
          v-else-if="homeState === 'passed'"
          type="success"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-trophy"
        >
          {{ t('student.languages.speakingJourney.assessment.home.passedBody') }}
        </v-alert>
        <v-alert
          v-else-if="homeState === 'failed' || homeState === 'abandoned' || homeState === 'timeout' || homeState === 'incomplete'"
          type="warning"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-clipboard-text-outline"
        >
          {{ t('student.languages.speakingJourney.assessment.home.terminalBody') }}
        </v-alert>
        <v-alert
          v-else
          type="success"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-lock-open-variant"
        >
          <div class="text-body-2 font-weight-medium mb-1">
            {{ t('student.languages.speakingJourney.assessment.whyUnlockedTitle') }}
          </div>
          <div class="text-body-2">
            {{ message || t('student.languages.speakingJourney.assessment.whyUnlockedBody') }}
          </div>
        </v-alert>

        <div class="d-flex flex-wrap gap-2">
          <v-btn
            v-if="homeState === 'in_progress'"
            color="primary"
            class="em-btn em-btn--primary spk-pressable"
            prepend-icon="mdi-play-circle-outline"
            :loading="sessionLoading"
            @click="$emit('resume')"
          >
            {{ t('student.languages.speakingJourney.assessment.home.resume') }}
          </v-btn>
          <v-btn
            v-else-if="homeState === 'eligible' || homeState === 'available'"
            color="primary"
            class="em-btn em-btn--primary spk-pressable"
            prepend-icon="mdi-rocket-launch"
            :loading="assessmentLoading || sessionLoading"
            @click="$emit('open-intro')"
          >
            {{ t('student.languages.speakingJourney.assessment.home.start') }}
          </v-btn>
          <v-btn
            v-else-if="['passed', 'failed', 'abandoned', 'timeout', 'incomplete', 'completed'].includes(homeState)"
            color="primary"
            class="em-btn em-btn--primary spk-pressable"
            prepend-icon="mdi-clipboard-check-outline"
            :loading="resultLoading"
            @click="$emit('view-result')"
          >
            {{ t('student.languages.speakingJourney.assessment.home.viewResult') }}
          </v-btn>
          <EmptyState
            v-else-if="homeState === 'locked'"
            compact
            icon="mdi-trophy-outline"
            :title="t('student.languages.speakingJourney.assessment.lockedTitle')"
            :description="message || t('student.languages.speakingJourney.assessment.lockedBody')"
            :action-label="t('student.languages.speakingJourney.runtime.backToJourney')"
            action-icon="mdi-arrow-left"
            @action="$emit('back-to-journey')"
          />
        </div>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import EmptyState from '../common/EmptyState.vue'
import SpeakingPromotionIntro from './SpeakingPromotionIntro.vue'
import SpeakingPromotionRuntime from './SpeakingPromotionRuntime.vue'
import SpeakingPromotionResult from './SpeakingPromotionResult.vue'

const props = defineProps({
  phase: { type: String, default: 'home' },
  homeState: { type: String, default: 'loading' },
  status: { type: Object, default: null },
  statusLoading: { type: Boolean, default: false },
  statusError: { type: String, default: '' },
  assessmentError: { type: String, default: '' },
  assessmentLoading: { type: Boolean, default: false },
  available: { type: Boolean, default: false },
  spaUnlocked: { type: Boolean, default: false },
  message: { type: String, default: '' },
  sourceCefr: { type: String, default: null },
  targetCefr: { type: String, default: null },
  estimatedDurationSeconds: { type: Number, default: 0 },
  taskCount: { type: Number, default: 0 },
  hasInteractionGaps: { type: Boolean, default: false },
  currentTask: { type: Object, default: null },
  completedTaskCount: { type: Number, default: 0 },
  remainingTaskCount: { type: Number, default: 0 },
  sessionLoading: { type: Boolean, default: false },
  sessionError: { type: String, default: '' },
  submitLoading: { type: Boolean, default: false },
  submitError: { type: String, default: '' },
  lastSubmit: { type: Object, default: null },
  actionLoading: { type: Boolean, default: false },
  result: { type: Object, default: null },
  resultLoading: { type: Boolean, default: false },
  resultError: { type: String, default: '' },
  canRetry: { type: Boolean, default: false },
  canPromote: { type: Boolean, default: false },
  promoteLoading: { type: Boolean, default: false },
  promoteError: { type: String, default: '' },
  promotionResult: { type: Object, default: null },
  officialPromoted: { type: Boolean, default: false },
})

defineEmits([
  'open-intro',
  'begin-tasks',
  'resume',
  'submit-task',
  'abandon',
  'retry',
  'view-result',
  'retry-status',
  'back-to-journey',
  'back-home',
  'promote',
])

const { t } = useI18n()

const stateLabel = computed(() => {
  const key = `student.languages.speakingJourney.assessment.home.states.${props.homeState}`
  const translated = t(key)
  return translated === key
    ? t('student.languages.speakingJourney.assessment.home.states.available')
    : translated
})

const stateChipColor = computed(() => {
  const map = {
    locked: 'warning',
    eligible: 'success',
    available: 'success',
    in_progress: 'primary',
    passed: 'success',
    failed: 'warning',
    abandoned: 'secondary',
    timeout: 'warning',
    incomplete: 'secondary',
    completed: 'secondary',
    error: 'error',
  }
  return map[props.homeState] || 'secondary'
})
</script>

<style scoped>
.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.stat-value {
  font-size: 1.1rem;
  font-weight: 800;
}
</style>
