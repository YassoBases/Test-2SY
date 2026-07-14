<template>
  <div :class="gridClasses" :aria-label="ariaLabel">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: {
    type: Number,
    default: 2,
    validator: (v) => [2, 3, 4, 5].includes(v),
  },
  ariaLabel: { type: String, default: '' },
})

const gridClasses = computed(() => [
  'tds-scope',
  'tds-summary-grid',
  props.columns > 2 && `tds-summary-grid--${props.columns}`,
])
</script>
