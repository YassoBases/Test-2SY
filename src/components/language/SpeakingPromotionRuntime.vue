<template>
  <div class="speaking-promotion-runtime speaking-runtime">
    <v-card class="glass-card pa-5 pa-md-6 mb-4" variant="flat">
      <div class="d-flex flex-wrap align-center justify-space-between gap-2 mb-3">
        <div>
          <div class="text-overline text-medium-emphasis mb-1">
            {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
          </div>
          <h2 class="text-h6 font-weight-bold mb-0">
            {{ t('student.languages.speakingJourney.assessment.runtime.title') }}
          </h2>
        </div>
        <v-chip size="small" variant="tonal" color="primary">
          {{
            t('student.languages.speakingJourney.assessment.runtime.progressChip', {
              current: Math.min(completedTaskCount + 1, taskCount || 1),
              total: taskCount || 1,
            })
          }}
        </v-chip>
      </div>

      <!-- Discrete task progress — no invented percentages -->
      <div
        class="progress-steps mb-4"
        role="list"
        :aria-label="t('student.languages.speakingJourney.assessment.runtime.progressLabel')"
      >
        <div
          v-for="n in taskCount"
          :key="n"
          class="progress-step"
          role="listitem"
          :class="{
            done: n <= completedTaskCount,
            current: n === completedTaskCount + 1,
          }"
          :aria-current="n === completedTaskCount + 1 ? 'step' : undefined"
        >
          <span class="progress-step__dot" aria-hidden="true" />
          <span class="progress-step__label">
            {{ t('student.languages.speakingJourney.assessment.taskOrder', { n }) }}
          </span>
        </div>
      </div>

      <p class="text-caption text-medium-emphasis mb-4">
        {{
          t('student.languages.speakingJourney.assessment.runtime.remaining', {
            n: remainingTaskCount,
          })
        }}
      </p>

      <v-alert v-if="sessionError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        <div class="d-flex flex-wrap align-center justify-space-between gap-2">
          <span>{{ sessionError }}</span>
          <v-btn size="small" variant="text" class="spk-pressable" @click="$emit('reconnect')">
            {{ t('student.languages.speakingJourney.assessment.runtime.reconnect') }}
          </v-btn>
        </div>
      </v-alert>
      <v-alert v-if="submitError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
        {{ submitError }}
      </v-alert>

      <LoadingState v-if="!currentTask && !sessionError" variant="cards" :count="1" class="spk-skeleton-block" />

      <template v-else-if="currentTask">
        <div class="d-flex flex-wrap gap-2 mb-3">
          <v-chip size="small" color="primary" variant="flat">
            {{
              t('student.languages.speakingJourney.assessment.taskOrder', {
                n: currentTask.task_order,
              })
            }}
          </v-chip>
          <v-chip size="small" variant="tonal">{{ formatFamily(currentTask.task_family) }}</v-chip>
          <v-chip size="small" variant="outlined">{{ currentTask.execution_mode }}</v-chip>
          <v-chip
            v-if="currentTask.spontaneous_production_required"
            size="small"
            color="secondary"
            variant="tonal"
          >
            {{ t('student.languages.speakingJourney.assessment.spontaneousProduction') }}
          </v-chip>
        </div>

        <div class="text-body-2 font-weight-medium mb-1" dir="auto">{{ currentTask.scenario }}</div>
        <p class="text-body-1 mb-3 english-island" dir="ltr">{{ currentTask.student_prompt }}</p>
        <div class="text-caption text-medium-emphasis mb-4">
          {{
            t('student.languages.speakingJourney.assessment.timing', {
              prep: currentTask.preparation_seconds || 0,
              max: currentTask.max_duration_seconds || 0,
            })
          }}
        </div>

        <v-alert
          v-if="submitPhase === 'waiting'"
          type="info"
          variant="tonal"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-timer-sand"
        >
          {{ t('student.languages.speakingJourney.assessment.runtime.waitingEval') }}
        </v-alert>
        <v-alert
          v-else-if="submitPhase === 'done' && lastSummary"
          type="success"
          variant="tonal"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-check"
        >
          {{ t('student.languages.speakingJourney.assessment.runtime.evalComplete') }}
          <div v-if="lastSummary" class="text-body-2 mt-1">{{ lastSummary }}</div>
        </v-alert>

        <SpeakingPromotionTaskRecorder
          v-if="submitPhase !== 'waiting'"
          :key="currentTask.task_id"
          :reset-key="currentTask.task_id"
          :execution-mode="currentTask.execution_mode"
          :min-seconds="1"
          :max-seconds="currentTask.max_duration_seconds || 90"
          :prep-seconds="currentTask.preparation_seconds || 0"
          :submitting="submitLoading"
          @submit="$emit('submit-task', $event)"
        />
      </template>

      <div class="d-flex flex-wrap gap-2 mt-4">
        <v-btn
          variant="text"
          color="error"
          class="spk-pressable"
          :loading="actionLoading"
          :disabled="submitLoading"
          @click="$emit('abandon')"
        >
          {{ t('student.languages.speakingJourney.assessment.runtime.abandon') }}
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import SpeakingPromotionTaskRecorder from './SpeakingPromotionTaskRecorder.vue'

const props = defineProps({
  currentTask: { type: Object, default: null },
  taskCount: { type: Number, default: 0 },
  completedTaskCount: { type: Number, default: 0 },
  remainingTaskCount: { type: Number, default: 0 },
  submitLoading: { type: Boolean, default: false },
  actionLoading: { type: Boolean, default: false },
  sessionError: { type: String, default: '' },
  submitError: { type: String, default: '' },
  lastSubmit: { type: Object, default: null },
})

defineEmits(['submit-task', 'abandon', 'reconnect'])

const { t } = useI18n()

const submitPhase = computed(() => {
  if (props.submitLoading) return 'waiting'
  // Only flash completion for the task that was just submitted.
  if (
    props.lastSubmit?.student_safe_summary &&
    props.lastSubmit?.task_id === props.currentTask?.task_id
  ) {
    return 'done'
  }
  return 'idle'
})
const lastSummary = computed(() =>
  props.lastSubmit?.task_id === props.currentTask?.task_id
    ? props.lastSubmit?.student_safe_summary || ''
    : '',
)

function formatFamily(family) {
  return String(family || '').replace(/_/g, ' ')
}
</script>

<style scoped>
.progress-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.progress-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  font-size: 0.75rem;
}
.progress-step__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(var(--v-theme-on-surface), 0.25);
}
.progress-step.done {
  border-color: rgba(var(--v-theme-success), 0.35);
}
.progress-step.done .progress-step__dot {
  background: rgb(var(--v-theme-success));
}
.progress-step.current {
  border-color: rgba(var(--v-theme-primary), 0.45);
  background: rgba(var(--v-theme-primary), 0.08);
}
.progress-step.current .progress-step__dot {
  background: rgb(var(--v-theme-primary));
}
.english-island {
  unicode-bidi: isolate;
}
</style>
