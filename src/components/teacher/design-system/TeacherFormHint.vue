<template>
  <div :class="hintClasses" role="note">
    <div class="tds-warning-card__content">
      <slot>{{ text }}</slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: { type: String, default: '' },
  variant: {
    type: String,
    default: 'info',
    validator: (v) => ['info', 'warning', 'error', 'success'].includes(v),
  },
})

const hintClasses = computed(() => [
  'tds-scope',
  'tds-form__hint',
  'tds-warning-card',
  `tds-warning-card--${props.variant}`,
])
</script>

<style scoped>
.tds-form__hint {
  margin: var(--em-teacher-helper-gap, 8px) 0 0;
}
</style>
