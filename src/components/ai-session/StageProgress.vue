<template>
  <div class="stage-progress" role="status">
    <span class="stage-progress__step">
      {{ t('student.grammarSession.progress.step', { current, total }) }}
    </span>
    <span class="stage-progress__time">
      {{ t('student.grammarSession.progress.elapsed', { time: formatted }) }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  current: { type: Number, default: 1 },
  total: { type: Number, default: 1 },
  elapsedSeconds: { type: Number, default: 0 },
})

const { t } = useI18n()

const formatted = computed(() => {
  const s = Math.max(0, Number(props.elapsedSeconds) || 0)
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${m}:${String(r).padStart(2, '0')}`
})
</script>

<style scoped>
.stage-progress {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.8125rem;
  color: var(--text-muted, #3f4f63);
}

.stage-progress__step {
  font-weight: 700;
  color: var(--text-primary, #0c1929);
}
</style>
