<template>
  <div :class="rootClasses" role="note">
    <div class="tds-warning-card__content">
      <p v-if="title" class="tds-warning-card__title">{{ title }}</p>
      <p v-if="message || $slots.default" class="tds-warning-card__body">
        <slot>{{ message }}</slot>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'info',
    validator: (v) => ['info', 'warning', 'error', 'success'].includes(v),
  },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
})

const rootClasses = computed(() => [
  'tds-scope',
  'tds-warning-card',
  `tds-warning-card--${props.variant}`,
])
</script>

<style scoped>
.tds-warning-card__content {
  flex: 1;
  min-width: 0;
}
</style>
