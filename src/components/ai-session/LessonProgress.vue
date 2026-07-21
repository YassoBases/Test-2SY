<template>
  <div
    class="lesson-progress"
    role="progressbar"
    :aria-valuenow="clamped"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-label="t('student.grammarSession.progress.session', { n: clamped })"
  >
    <div class="lesson-progress__track">
      <div class="lesson-progress__fill" :style="{ width: `${clamped}%` }" />
    </div>
    <span class="lesson-progress__label">{{ clamped }}%</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  percent: { type: Number, default: 0 },
})

const { t } = useI18n()
const clamped = computed(() => Math.min(100, Math.max(0, Math.round(props.percent || 0))))
</script>

<style scoped>
.lesson-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-width: 120px;
}

.lesson-progress__track {
  flex: 1;
  height: 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  overflow: hidden;
}

.lesson-progress__fill {
  height: 100%;
  border-radius: inherit;
  background: var(--color-primary, #6366f1);
  transition: width 280ms ease-out;
}

.lesson-progress__label {
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 2.5rem;
  text-align: end;
}

@media (prefers-reduced-motion: reduce) {
  .lesson-progress__fill {
    transition: none;
  }
}
</style>
