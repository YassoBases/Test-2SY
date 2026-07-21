<template>
  <section class="lesson-progress glass-card pa-4 pa-md-5 mb-5" :aria-label="t('student.languages.speakingJourney.progress.title')">
    <div class="d-flex flex-wrap align-center justify-space-between gap-3 mb-3">
      <div>
        <div class="text-subtitle-2 font-weight-bold mb-1">
          {{ t('student.languages.speakingJourney.progress.title') }}
        </div>
        <div v-if="missionPosition && missionTotal" class="text-body-2 text-medium-emphasis">
          {{
            t('student.languages.speakingJourney.mission.position', {
              position: missionPosition,
              total: missionTotal,
            })
          }}
        </div>
        <div v-if="sessionPhase" class="text-caption text-medium-emphasis mt-1">
          {{ phaseLabel }}
        </div>
      </div>
      <v-chip size="small" variant="tonal" color="primary">
        {{
          t('student.languages.speakingJourney.progress.remaining', {
            n: activitiesRemaining,
          })
        }}
      </v-chip>
    </div>

    <ol v-if="stepper.length" class="activity-stepper mb-3" aria-label="activity steps">
      <li
        v-for="(step, idx) in stepper"
        :key="step.step_id || idx"
        class="stepper-item"
        :class="`stepper-item--${stepStatus(step)}`"
        :title="step.label"
      >
        <span class="stepper-dot" aria-hidden="true">
          <v-icon size="14">{{ stepIcon(step) }}</v-icon>
        </span>
        <span class="stepper-label">{{ step.label }}</span>
      </li>
    </ol>

    <v-progress-linear
      :model-value="percent"
      color="primary"
      height="8"
      rounded
      class="mb-3"
      :aria-valuenow="percent"
      aria-valuemin="0"
      aria-valuemax="100"
      role="progressbar"
      :aria-label="t('student.languages.speakingJourney.progress.title')"
    />

    <div class="d-flex flex-wrap gap-3 text-caption text-medium-emphasis">
      <span>
        {{ t('student.languages.speakingJourney.progress.completed', { n: activitiesCompleted }) }}
        /
        {{ activitiesTotal }}
      </span>
      <span v-if="currentActivityTitle" class="current-activity">
        {{ t('student.languages.speakingJourney.progress.current') }}:
        <strong class="text-high-emphasis">{{ currentActivityTitle }}</strong>
      </span>
      <v-chip
        v-if="currentActivityKind"
        size="x-small"
        variant="tonal"
        :color="kindColor"
        prepend-icon="mdi-shape-outline"
      >
        {{ kindLabel }}
      </v-chip>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { activityMeta } from '../../utils/speakingRuntimeMeta.js'

const props = defineProps({
  currentMission: { type: Object, default: null },
  currentActivityTitle: { type: String, default: '' },
  currentActivityKind: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
  todaySteps: { type: Array, default: () => [] },
  sessionPhase: { type: String, default: '' },
})

const { t } = useI18n()

const missionPosition = computed(() => props.currentMission?.position || 0)
const missionTotal = computed(() => props.currentMission?.total || 0)
const stepper = computed(() => props.todaySteps || [])
const kindMeta = computed(() => activityMeta(props.currentActivityKind))
const kindColor = computed(() => kindMeta.value.color)
const kindLabel = computed(() => {
  const stage = kindMeta.value.stage
  return t(`student.languages.speakingJourney.runtime.stages.${stage}`)
})
const phaseLabel = computed(() => {
  const phase = String(props.sessionPhase || '').trim()
  if (!phase) return ''
  const key = `student.languages.speakingJourney.progress.phases.${phase}`
  const translated = t(key)
  return translated === key
    ? t('student.languages.speakingJourney.progress.phaseGeneric', { phase })
    : translated
})

const percent = computed(() => {
  const total = props.activitiesTotal
  if (!total) return 0
  return Math.min(100, Math.round((props.activitiesCompleted / total) * 100))
})

function stepStatus(step) {
  const s = String(step.status || '').toLowerCase()
  if (s === 'done' || s === 'completed') return 'done'
  if (s === 'active' || s === 'current') return 'active'
  return 'upcoming'
}

function stepIcon(step) {
  const status = stepStatus(step)
  if (status === 'done') return 'mdi-check'
  if (status === 'active') return activityMeta(step.kind).icon
  return 'mdi-circle-outline'
}
</script>

<style scoped>
.lesson-progress {
  border-radius: var(--em-radius-md, 16px);
}
.current-activity strong {
  font-weight: 700;
}
.activity-stepper {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.stepper-item {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  max-width: 160px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid transparent;
}
.stepper-item--active {
  background: rgba(var(--v-theme-primary), 0.1);
  border-color: rgba(var(--v-theme-primary), 0.25);
}
.stepper-item--done {
  background: rgba(var(--v-theme-success), 0.1);
}
.stepper-label {
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.stepper-dot {
  width: 18px;
  height: 18px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
</style>
