<template>
  <div :class="groupClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  align: {
    type: String,
    default: 'start',
    validator: (v) => ['start', 'end', 'split'].includes(v),
  },
})

const groupClasses = computed(() => [
  'tds-scope',
  'tds-btn-group',
  props.align === 'end' && 'tds-btn-group--end',
  props.align === 'split' && 'tds-btn-group--split',
])
</script>
