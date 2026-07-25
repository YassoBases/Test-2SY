<template>
  <div class="listen-hero glass-card mb-4">
    <div class="listen-hero__glow" aria-hidden="true" />
    <div class="listen-hero__badge">
      <v-icon size="28" color="secondary">mdi-headphones</v-icon>
      <span class="listen-hero__cefr">{{ officialLevel }}</span>
    </div>
    <div class="listen-hero__copy min-w-0">
      <p class="listen-hero__kicker mb-1">{{ t('student.languages.coach.ux.hero.eyebrow') }}</p>
      <h2 class="listen-hero__title">{{ t('student.languages.coach.ux.hero.title') }}</h2>
      <p v-if="journeyHeadline" class="listen-hero__hint mb-0">{{ journeyHeadline }}</p>
      <div class="listen-hero__stats">
        <div class="listen-stat">
          <span class="listen-stat__value">{{ officialLevel }}</span>
          <span class="listen-stat__label">{{ t('student.languages.coach.ux.hero.officialLevel') }}</span>
        </div>
        <div class="listen-stat">
          <span class="listen-stat__value listen-stat__value--sm">{{ currentStep }}</span>
          <span class="listen-stat__label">{{ t('student.languages.coach.ux.hero.currentStep') }}</span>
        </div>
        <div class="listen-stat">
          <span class="listen-stat__value">{{ journeyTargetLabel }}</span>
          <span class="listen-stat__label">{{ t('student.languages.coach.ux.hero.goal') }}</span>
        </div>
      </div>
    </div>
    <div class="listen-hero__progress">
      <div class="d-flex align-center justify-space-between mb-2 gap-2">
        <span class="text-body-2 font-weight-medium">{{ progressMessage }}</span>
        <span class="listen-hero__pct">{{ progressPercent }}%</span>
      </div>
      <v-progress-linear
        :model-value="progressPercent"
        color="secondary"
        height="10"
        rounded
      />
      <div v-if="nextMilestone" class="d-flex align-center gap-2 text-caption text-medium-emphasis mt-2">
        <v-icon size="16" color="secondary">mdi-flag-checkered</v-icon>
        <span>{{ nextMilestone }}</span>
      </div>
    </div>
  </div>
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
.listen-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem 1.35rem;
  padding: 1.25rem 1.35rem;
  align-items: center;
}

.listen-hero__glow {
  position: absolute;
  inset: -35% auto auto -8%;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(var(--v-theme-secondary), 0.2), transparent 68%);
  pointer-events: none;
}

.listen-hero__badge {
  position: relative;
  z-index: 1;
  width: 88px;
  height: 88px;
  border-radius: 26px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  background: linear-gradient(145deg, rgba(var(--v-theme-secondary), 0.26), rgba(var(--v-theme-primary), 0.1));
  border: 1px solid rgba(var(--v-theme-secondary), 0.32);
}

.listen-hero__cefr {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
  color: rgb(var(--v-theme-secondary));
}

.listen-hero__copy {
  position: relative;
  z-index: 1;
}

.listen-hero__kicker {
  font-size: 0.72rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.listen-hero__title {
  font-size: 1.3rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem;
  line-height: 1.3;
}

.listen-hero__hint {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.listen-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem 1.2rem;
  margin-top: 0.85rem;
}

.listen-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.listen-stat__value {
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.listen-stat__value--sm {
  font-size: 0.92rem;
}

.listen-stat__label {
  font-size: 0.68rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.listen-hero__progress {
  position: relative;
  z-index: 1;
  grid-column: 1 / -1;
  padding-top: 0.35rem;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.listen-hero__pct {
  font-weight: 800;
  color: rgb(var(--v-theme-secondary));
}

.min-w-0 {
  min-width: 0;
}

@media (max-width: 640px) {
  .listen-hero {
    grid-template-columns: 1fr;
  }
}
</style>
