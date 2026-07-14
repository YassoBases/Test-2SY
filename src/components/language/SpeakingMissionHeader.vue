<template>
  <header class="mission-header glass-card pa-5 pa-md-6 mb-5" aria-labelledby="speaking-mission-heading">
    <div class="text-overline text-medium-emphasis mb-1">
      {{ t('student.languages.speakingJourney.lesson.eyebrow') }}
    </div>
    <h2 id="speaking-mission-heading" class="text-h5 font-weight-bold mb-2">
      {{ lessonTitle || focusLabel || t('student.languages.speakingJourney.hero.emptyFocus') }}
    </h2>
    <p v-if="focusReason || planSummary" class="text-body-2 text-medium-emphasis mb-4">
      {{ focusReason || planSummary }}
    </p>

    <v-row dense>
      <v-col cols="12" sm="6" md="4">
        <div class="meta-label">{{ t('student.languages.speakingJourney.mission.title') }}</div>
        <div class="meta-value">{{ missionTitle }}</div>
        <div v-if="missionPurpose" class="text-caption text-medium-emphasis mt-1">{{ missionPurpose }}</div>
      </v-col>
      <v-col cols="6" sm="3" md="2">
        <div class="meta-label">{{ t('student.languages.speakingJourney.hero.level') }}</div>
        <div class="meta-value" dir="ltr">{{ officialCefr || '—' }}</div>
      </v-col>
      <v-col cols="6" sm="3" md="2">
        <div class="meta-label">{{ t('student.languages.speakingJourney.lesson.mode') }}</div>
        <div class="meta-value meta-value--sm">{{ taskMode || '—' }}</div>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <div class="meta-label">{{ t('student.languages.speakingJourney.attempt.label') }}</div>
        <div class="d-flex flex-wrap gap-2 align-center mt-1">
          <template v-if="attempt">
            <v-chip size="small" :color="attempt.is_retry ? 'warning' : 'primary'" variant="tonal">
              {{
                attempt.is_retry
                  ? t('student.languages.speakingJourney.attempt.retry', { n: attempt.attempt_number })
                  : t('student.languages.speakingJourney.attempt.first', { n: attempt.attempt_number })
              }}
            </v-chip>
            <span class="text-body-2">{{ attempt.message }}</span>
          </template>
          <span v-else class="text-body-2 text-medium-emphasis">—</span>
        </div>
      </v-col>
    </v-row>

    <ul v-if="objectives.length" class="objectives mt-4 mb-0">
      <li v-for="(obj, i) in objectives" :key="i">{{ obj }}</li>
    </ul>
    <p v-if="expectedOutcome" class="text-body-2 mt-3 mb-0">{{ expectedOutcome }}</p>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  lessonTitle: { type: String, default: '' },
  focusLabel: { type: String, default: '' },
  focusReason: { type: String, default: '' },
  planSummary: { type: String, default: '' },
  officialCefr: { type: String, default: '' },
  currentMission: { type: Object, default: null },
  nextMission: { type: Object, default: null },
  currentTask: { type: Object, default: null },
  attempt: { type: Object, default: null },
  objectives: { type: Array, default: () => [] },
  expectedOutcome: { type: String, default: '' },
})

const { t } = useI18n()

const missionTitle = computed(
  () => props.currentMission?.title || props.nextMission?.title || props.focusLabel || '—',
)
const missionPurpose = computed(
  () => props.currentMission?.purpose || props.nextMission?.purpose || '',
)
const taskMode = computed(
  () => props.currentTask?.execution_mode || props.currentMission?.execution_mode || '',
)
</script>

<style scoped>
.mission-header {
  border-radius: var(--em-radius-md, 16px);
}
.meta-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.meta-value {
  font-size: 1.05rem;
  font-weight: 700;
}
.meta-value--sm {
  font-size: 0.95rem;
}
.objectives {
  margin: 0;
  padding-inline-start: 1.25rem;
}
</style>
