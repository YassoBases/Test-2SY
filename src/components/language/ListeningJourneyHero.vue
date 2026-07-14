<template>
  <v-card class="journey-hero pa-6 pa-md-8 mb-6" variant="flat">
    <div class="d-flex align-start gap-4 mb-6">
      <div class="hero-icon-wrap flex-shrink-0">
        <span class="hero-emoji" aria-hidden="true">🎧</span>
      </div>
      <div class="flex-grow-1 min-width-0">
        <div class="text-overline text-medium-emphasis mb-1">
          {{ t('student.languages.coach.ux.hero.eyebrow') }}
        </div>
        <h2 class="text-h4 font-weight-bold mb-0">{{ t('student.languages.coach.ux.hero.title') }}</h2>
      </div>
    </div>

    <v-row class="hero-stats mb-5" dense>
      <v-col cols="12" sm="4">
        <div class="hero-stat">
          <div class="hero-stat-label">{{ t('student.languages.coach.ux.hero.officialLevel') }}</div>
          <div class="hero-stat-value">{{ officialLevel }}</div>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="hero-stat">
          <div class="hero-stat-label">{{ t('student.languages.coach.ux.hero.currentStep') }}</div>
          <div class="hero-stat-value hero-stat-value--sm">{{ currentStep }}</div>
        </div>
      </v-col>
      <v-col cols="12" sm="4">
        <div class="hero-stat">
          <div class="hero-stat-label">{{ t('student.languages.coach.ux.hero.goal') }}</div>
          <div class="hero-stat-value">{{ journeyTargetLabel }}</div>
        </div>
      </v-col>
    </v-row>

    <p class="text-body-1 hero-sentence mb-5">{{ journeyHeadline }}</p>

    <div class="hero-progress">
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-body-2 font-weight-medium">{{ progressMessage }}</span>
        <span class="text-h6 font-weight-bold progress-pct">{{ progressPercent }}%</span>
      </div>
      <v-progress-linear
        :model-value="progressPercent"
        color="secondary"
        height="12"
        rounded
        class="mb-3"
      />
      <div v-if="nextMilestone" class="d-flex align-center gap-2 text-body-2 text-medium-emphasis">
        <v-icon size="18" color="secondary">mdi-flag-checkered</v-icon>
        <span>{{ nextMilestone }}</span>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  journey: { type: Object, default: null },
})

const { t } = useI18n()

const narrative = computed(() => props.journey?.narrative || {})
const timelineSteps = computed(() => narrative.value.timeline_steps || [])

const officialLevel = computed(() => props.journey?.official_level || '—')
const journeyTargetLabel = computed(() => props.journey?.journey_target?.label || '—')
const currentStep = computed(() => narrative.value.current_step_label || '—')
const journeyHeadline = computed(() => narrative.value.journey_headline || '')
const progressMessage = computed(() => narrative.value.promotion_progress_message || '')

const progressPercent = computed(() => {
  const steps = timelineSteps.value
  if (!steps.length) return 0
  const done = steps.filter((s) => s.done).length
  return Math.round((done / steps.length) * 100)
})

const nextMilestone = computed(() => {
  const next = timelineSteps.value.find((s) => !s.done)
  return next?.label || ''
})
</script>

<style scoped>
.journey-hero {
  border-radius: 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-secondary), 0.12) 0%,
    rgba(var(--v-theme-surface), 1) 55%
  );
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.hero-icon-wrap {
  width: 4rem;
  height: 4rem;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-secondary), 0.15);
}
.hero-emoji {
  font-size: 2rem;
  line-height: 1;
}
.hero-stat {
  padding: 0.75rem 0;
}
.hero-stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 0.25rem;
}
.hero-stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1.15;
  color: rgb(var(--v-theme-on-surface));
}
.hero-stat-value--sm {
  font-size: 1.125rem;
  font-weight: 700;
}
.hero-sentence {
  line-height: 1.6;
  max-width: 42rem;
}
.progress-pct {
  color: rgb(var(--v-theme-secondary));
}
.min-width-0 {
  min-width: 0;
}
</style>
