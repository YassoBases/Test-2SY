<template>
  <section class="lesson-progress glass-card pa-4 pa-md-5 mb-5" aria-label="lesson progress">
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
      </div>
      <v-chip size="small" variant="tonal" color="primary">
        {{
          t('student.languages.speakingJourney.progress.remaining', {
            n: activitiesRemaining,
          })
        }}
      </v-chip>
    </div>

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
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  currentMission: { type: Object, default: null },
  currentActivityTitle: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
})

const { t } = useI18n()

const missionPosition = computed(() => props.currentMission?.position || 0)
const missionTotal = computed(() => props.currentMission?.total || 0)

const percent = computed(() => {
  const total = props.activitiesTotal
  if (!total) return 0
  return Math.min(100, Math.round((props.activitiesCompleted / total) * 100))
})
</script>

<style scoped>
.lesson-progress {
  border-radius: var(--em-radius-md, 16px);
}
.current-activity strong {
  font-weight: 700;
}
</style>
