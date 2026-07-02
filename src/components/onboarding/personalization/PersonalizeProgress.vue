<template>
  <div
    class="personalize-progress"
    role="status"
    :aria-label="t('auth.onboarding.progress.aria', { step, total, remaining: remainingLabel })"
  >
    <div class="personalize-progress__meta">
      <span class="personalize-progress__label">
        {{ t('auth.onboarding.progress.stepOf', { step, total }) }}
      </span>
      <span class="personalize-progress__remaining">{{ remainingLabel }}</span>
    </div>
    <div class="personalize-progress__track" aria-hidden="true">
      <div class="personalize-progress__fill" :style="{ width: `${percent}%` }" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  step: { type: Number, required: true },
  total: { type: Number, required: true },
})

const { t } = useI18n()

const percent = computed(() => Math.round((props.step / props.total) * 100))

const remainingLabel = computed(() => {
  if (props.step >= props.total) return t('auth.onboarding.progress.lastStep')
  const left = props.total - props.step
  if (left === 1) return t('auth.onboarding.progress.oneLeft')
  return t('auth.onboarding.progress.stepsLeft', { n: left })
})
</script>
