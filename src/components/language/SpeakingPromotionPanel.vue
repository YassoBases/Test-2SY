<template>
  <div class="speaking-promotion">
    <v-alert v-if="statusError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      {{ statusError }}
    </v-alert>
    <v-alert v-if="blueprintError" type="error" variant="tonal" class="mb-4 rounded-lg" role="alert">
      {{ blueprintError }}
    </v-alert>

    <LoadingState v-if="statusLoading && !status" variant="cards" :count="2" />

    <template v-else>
      <v-card class="glass-card pa-6 mb-6" variant="flat">
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.speakingJourney.assessment.eyebrow') }}
        </div>
        <h2 class="text-h5 font-weight-bold mb-2">
          {{ t('student.languages.speakingJourney.assessment.title') }}
        </h2>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ message || t('student.languages.speakingJourney.assessment.defaultMessage') }}
        </p>

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
            <div class="stat-label">{{ t('student.languages.speakingJourney.assessment.state') }}</div>
            <div class="stat-value d-inline-flex align-center gap-1">
              <v-icon size="18" :color="spaUnlocked ? 'success' : 'warning'" aria-hidden="true">
                {{ spaUnlocked ? 'mdi-lock-open-variant' : 'mdi-lock-outline' }}
              </v-icon>
              {{ spaUnlocked
                ? t('student.languages.speakingJourney.assessment.unlocked')
                : t('student.languages.speakingJourney.assessment.locked') }}
            </div>
          </v-col>
        </v-row>

        <v-alert
          v-if="!spaUnlocked"
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

        <v-alert
          type="info"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-information-outline"
        >
          {{ t('student.languages.speakingJourney.assessment.previewOnly') }}
        </v-alert>

        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ t('student.languages.speakingJourney.assessment.whatNext') }}
        </p>

        <v-btn
          v-if="spaUnlocked || available"
          color="primary"
          class="em-btn em-btn--primary"
          :loading="blueprintLoading"
          prepend-icon="mdi-eye-outline"
          @click="$emit('preview')"
        >
          {{
            blueprint
              ? t('student.languages.speakingJourney.assessment.refreshPreview')
              : t('student.languages.speakingJourney.assessment.previewCta')
          }}
        </v-btn>
        <EmptyState
          v-else
          compact
          icon="mdi-trophy-outline"
          :title="t('student.languages.speakingJourney.assessment.lockedTitle')"
          :description="message || t('student.languages.speakingJourney.assessment.lockedBody')"
        />
      </v-card>

      <v-card v-if="blueprint" class="glass-card pa-5 mb-6" variant="flat">
        <div class="d-flex flex-wrap align-center justify-space-between gap-2 mb-4">
          <div class="text-subtitle-1 font-weight-bold mb-0">
            {{ t('student.languages.speakingJourney.assessment.blueprintTitle') }}
          </div>
          <v-chip size="small" variant="tonal" color="primary">
            {{ t('student.languages.speakingJourney.assessment.taskCount', { n: tasks.length }) }}
          </v-chip>
        </div>

        <v-alert
          v-if="hasInteractionGaps"
          type="warning"
          variant="tonal"
          density="comfortable"
          class="mb-4 rounded-lg"
          prepend-icon="mdi-account-voice-off"
        >
          {{ t('student.languages.speakingJourney.assessment.interactionGapNote') }}
        </v-alert>

        <div class="task-list">
          <article
            v-for="task in tasks"
            :key="task.task_id"
            class="task-card pa-4 rounded-lg"
          >
            <div class="d-flex flex-wrap gap-2 mb-2">
              <v-chip size="small" color="primary" variant="flat">
                {{ t('student.languages.speakingJourney.assessment.taskOrder', { n: task.task_order }) }}
              </v-chip>
              <v-chip size="small" variant="tonal">{{ formatFamily(task.task_family) }}</v-chip>
              <v-chip size="small" variant="outlined">{{ task.execution_mode }}</v-chip>
              <v-chip
                v-if="task.spontaneous_production_required"
                size="small"
                color="secondary"
                variant="tonal"
              >
                {{ t('student.languages.speakingJourney.assessment.spontaneousProduction') }}
              </v-chip>
            </div>
            <div class="text-body-2 font-weight-medium mb-1" dir="auto">{{ task.scenario }}</div>
            <p class="text-body-2 mb-2 english-island" dir="ltr">{{ task.student_prompt }}</p>
            <div class="text-caption text-medium-emphasis">
              {{
                t('student.languages.speakingJourney.assessment.timing', {
                  prep: task.preparation_seconds || 0,
                  max: task.max_duration_seconds || 0,
                })
              }}
            </div>
            <ul v-if="task.follow_up_prompts?.length" class="followups mt-2">
              <li v-for="(fu, i) in task.follow_up_prompts" :key="i" dir="ltr">{{ fu }}</li>
            </ul>
          </article>
        </div>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import EmptyState from '../common/EmptyState.vue'

defineProps({
  status: { type: Object, default: null },
  statusLoading: { type: Boolean, default: false },
  statusError: { type: String, default: '' },
  blueprint: { type: Object, default: null },
  blueprintLoading: { type: Boolean, default: false },
  blueprintError: { type: String, default: '' },
  available: { type: Boolean, default: false },
  spaUnlocked: { type: Boolean, default: false },
  message: { type: String, default: '' },
  sourceCefr: { type: String, default: null },
  targetCefr: { type: String, default: null },
  estimatedDurationSeconds: { type: Number, default: 0 },
  tasks: { type: Array, default: () => [] },
  hasInteractionGaps: { type: Boolean, default: false },
})

defineEmits(['preview'])

const { t } = useI18n()

function formatFamily(family) {
  return String(family || '').replace(/_/g, ' ')
}
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
.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.task-card {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.english-island {
  unicode-bidi: isolate;
}
.followups {
  margin: 0;
  padding-inline-start: 1.25rem;
  font-size: 0.875rem;
}
</style>
