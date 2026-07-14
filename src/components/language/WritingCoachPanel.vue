<template>
  <v-card v-if="hasCoach" class="coach-panel pa-6 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-avatar color="secondary" variant="tonal" size="40">
        <v-icon>mdi-account-voice</v-icon>
      </v-avatar>
      <div>
        <div class="text-overline text-medium-emphasis">{{ t('student.languages.writingJourney.coach.eyebrow') }}</div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.writingJourney.coach.title') }}</h3>
      </div>
    </div>

    <v-alert v-if="encouragement" type="info" variant="tonal" density="comfortable" class="mb-4 rounded-lg">
      {{ encouragement }}
    </v-alert>

    <div v-if="mainIssue" class="coach-block mb-3">
      <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.coach.mainIssue') }}</div>
      <p class="text-body-1 mb-0" dir="ltr">{{ mainIssue }}</p>
    </div>

    <div v-if="whyItMatters" class="coach-block mb-3">
      <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.writingJourney.coach.whyItMatters') }}</div>
      <p class="text-body-2 mb-0" dir="ltr">{{ whyItMatters }}</p>
    </div>

    <div v-if="mission" class="mission-block mb-3">
      <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.coach.mission') }}</div>
      <p class="text-body-1 mb-0 mission-text" dir="ltr">{{ mission }}</p>
    </div>

    <div v-if="beforeExample || afterExample" class="example-block">
      <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.coach.example') }}</div>
      <div v-if="beforeExample" class="example-row before" dir="ltr">
        <span class="example-tag">{{ t('student.languages.writingJourney.coach.beforeLabel') }}</span>
        <span class="text-body-2">{{ beforeExample }}</span>
      </div>
      <div v-if="afterExample" class="example-row after" dir="ltr">
        <span class="example-tag">{{ t('student.languages.writingJourney.coach.afterLabel') }}</span>
        <span class="text-body-2">{{ afterExample }}</span>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  hasCoach: { type: Boolean, default: false },
  encouragement: { type: String, default: '' },
  mainIssue: { type: String, default: '' },
  whyItMatters: { type: String, default: '' },
  mission: { type: String, default: '' },
  beforeExample: { type: String, default: '' },
  afterExample: { type: String, default: '' },
})

const { t } = useI18n()
</script>

<style scoped>
.coach-panel {
  border-radius: 20px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.15);
}
.coach-block {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.04);
}
.mission-block {
  padding: 1rem 1.15rem;
  border-radius: 14px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.25);
  background: rgba(var(--v-theme-secondary), 0.06);
}
.mission-text {
  font-weight: 500;
}
.example-block {
  padding: 1rem 1.15rem;
  border-radius: 14px;
  background: rgba(var(--v-theme-on-surface), 0.04);
}
.example-row {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  padding: 0.35rem 0;
}
.example-tag {
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  min-width: 3.5rem;
}
.example-row.before .example-tag {
  color: rgb(var(--v-theme-error));
}
.example-row.after .example-tag {
  color: rgb(var(--v-theme-success));
}
.example-row.before .text-body-2 {
  text-decoration: line-through;
  opacity: 0.75;
}
</style>
