<template>
  <div
    class="lesson-progress-mini"
    :class="{ 'lesson-progress-mini--row': variant === 'row' }"
    :aria-label="`${label} ${safePercent}%`"
  >
    <span v-if="label && variant === 'row'" class="lesson-progress-mini__label">{{ label }}</span>
    <div class="lesson-progress-mini__bar">
      <div class="lesson-progress-mini__track" aria-hidden="true">
        <div class="lesson-progress-mini__fill" :style="{ width: `${safePercent}%` }" />
      </div>
      <span class="lesson-progress-mini__value">{{ safePercent }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percent: { type: Number, default: 0 },
  label: { type: String, default: '' },
  variant: { type: String, default: 'inline' },
})

const safePercent = computed(() => Math.min(100, Math.max(0, Number(props.percent) || 0)))
</script>
