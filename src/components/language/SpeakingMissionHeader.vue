<template>
  <header class="mission-header glass-card pa-5 pa-md-6 mb-5" aria-labelledby="speaking-mission-heading">
    <div class="d-flex align-start gap-3 mb-3">
      <div class="mission-icon" aria-hidden="true">
        <v-icon :color="kindColor" size="26">{{ kindIcon }}</v-icon>
      </div>
      <div class="min-width-0 flex-grow-1">
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.speakingJourney.lesson.eyebrow') }}
        </div>
        <h2 id="speaking-mission-heading" class="text-h5 font-weight-bold mb-2">
          {{ lessonTitle || focusLabel || t('student.languages.speakingJourney.hero.emptyFocus') }}
        </h2>
        <p v-if="focusReason || planSummary" class="text-body-2 text-medium-emphasis mb-0">
          {{ focusReason || planSummary }}
        </p>
      </div>
    </div>

    <div class="mission-spotlight rounded-lg pa-4 mb-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.mission.title') }}
      </div>
      <div class="text-h6 font-weight-bold mb-1">{{ missionTitle }}</div>
      <div v-if="missionPurpose" class="text-body-2 text-medium-emphasis mb-2">{{ missionPurpose }}</div>
      <div class="d-flex flex-wrap gap-2">
        <v-chip v-if="stageLabel" size="small" :color="kindColor" variant="tonal" :prepend-icon="kindIcon">
          {{ stageLabel }}
        </v-chip>
        <v-chip
          v-if="currentMission?.uses_alex || liveExecutionReady"
          size="small"
          color="secondary"
          variant="tonal"
          prepend-icon="mdi-account-voice"
        >
          {{ t('student.languages.speakingJourney.mission.usesAlex') }}
        </v-chip>
        <v-chip
          v-if="missionPosition && missionTotal"
          size="small"
          variant="outlined"
        >
          {{
            t('student.languages.speakingJourney.mission.position', {
              position: missionPosition,
              total: missionTotal,
            })
          }}
        </v-chip>
      </div>
    </div>

    <v-row dense>
      <v-col cols="6" sm="3" md="2">
        <div class="meta-label">{{ t('student.languages.speakingJourney.hero.level') }}</div>
        <div class="meta-value" dir="ltr">{{ officialCefr || '—' }}</div>
      </v-col>
      <v-col cols="6" sm="3" md="3">
        <div class="meta-label">{{ t('student.languages.speakingJourney.lesson.mode') }}</div>
        <div class="meta-value meta-value--sm">{{ taskModeLabel || '—' }}</div>
      </v-col>
      <v-col cols="12" sm="6" md="7">
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
            <v-chip
              v-if="attempt.completed_task_attempt_count != null"
              size="small"
              variant="outlined"
            >
              {{
                t('student.languages.speakingJourney.attempt.completedTasks', {
                  n: attempt.completed_task_attempt_count,
                })
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

    <div v-if="nextMissionDisplayTitle" class="next-hint text-caption text-medium-emphasis mt-4">
      {{ t('student.languages.speakingJourney.path.next') }}:
      <strong class="text-high-emphasis">{{ nextMissionDisplayTitle }}</strong>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { activityMeta } from '../../utils/speakingRuntimeMeta.js'
import {
  educationalMissionInstructions,
  educationalMissionTitle,
} from '../../utils/speakingFraming.js'

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
  activityKind: { type: String, default: '' },
  liveExecutionReady: { type: Boolean, default: false },
})

const { t } = useI18n()

const storyTitle = computed(() => props.lessonTitle || props.focusLabel || '')
const missionTitle = computed(() =>
  educationalMissionTitle(
    props.currentMission?.title || props.nextMission?.title,
    storyTitle.value,
    t,
  ),
)
const missionPurpose = computed(() =>
  educationalMissionInstructions(
    props.currentMission?.purpose || props.nextMission?.purpose || '',
  ),
)
const missionPosition = computed(() => props.currentMission?.position || 0)
const missionTotal = computed(() => props.currentMission?.total || 0)
const taskMode = computed(
  () => props.currentTask?.execution_mode || props.currentMission?.execution_mode || '',
)
const taskModeLabel = computed(() => {
  const m = String(taskMode.value || '').toLowerCase()
  if (!m) return ''
  const key = `student.languages.speakingJourney.task.modes.${m}`
  const translated = t(key)
  return translated === key ? taskMode.value : translated
})
const meta = computed(() => activityMeta(props.activityKind))
const kindIcon = computed(() => meta.value.icon)
const kindColor = computed(() => meta.value.color)
const stageLabel = computed(() =>
  t(`student.languages.speakingJourney.runtime.stages.${meta.value.stage}`),
)
const nextMissionDisplayTitle = computed(() => {
  if (!props.nextMission?.title) return ''
  return educationalMissionTitle(props.nextMission.title, storyTitle.value, t)
})
</script>

<style scoped>
.mission-header {
  border-radius: var(--em-radius-md, 16px);
}
.mission-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-primary), 0.1);
  flex-shrink: 0;
}
.mission-spotlight {
  background: rgba(var(--v-theme-primary), 0.06);
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
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
.min-width-0 {
  min-width: 0;
}
</style>
