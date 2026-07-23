<template>
  <AppCard class="journey-progress" solid padding="md">
    <div class="journey-progress__meta">
      <span class="journey-progress__level">
        {{ t('student.englishJourney.progress.level', { cefr: progress?.cefr_label || '—' }) }}
      </span>
      <span class="journey-progress__stage">
        {{
          t('student.englishJourney.progress.stageOf', {
            index: progress?.stage_index || 0,
            total: progress?.stage_total_in_level || 0,
          })
        }}
      </span>
    </div>
    <div
      class="journey-progress__track"
      role="progressbar"
      :aria-valuenow="percent"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="t('student.englishJourney.progress.level', { cefr: progress?.cefr_label || '' })"
    >
      <div class="journey-progress__fill" :style="{ width: `${percent}%` }" />
    </div>
    <p class="journey-progress__overall text-medium-emphasis">
      {{
        t('student.englishJourney.progress.overall', {
          done: progress?.overall_completed || 0,
          total: progress?.overall_total || 0,
        })
      }}
    </p>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'

const props = defineProps({
  progress: { type: Object, default: null },
})

const { t } = useI18n()
const percent = computed(() => Math.max(0, Math.min(100, Number(props.progress?.level_percent) || 0)))
</script>

<style scoped>
.journey-progress__meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.journey-progress__track {
  height: 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  overflow: hidden;
}

.journey-progress__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #6366f1, #7c3aed);
  transition: width 280ms ease-out;
}

.journey-progress__overall {
  margin: 12px 0 0;
  font-size: 0.8125rem;
}

@media (prefers-reduced-motion: reduce) {
  .journey-progress__fill {
    transition: none;
  }
}
</style>
