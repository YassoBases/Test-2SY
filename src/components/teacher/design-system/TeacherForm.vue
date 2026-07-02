<template>
  <div :class="rootClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  surface: { type: Boolean, default: true },
  lesson: { type: Boolean, default: false },
})

const rootClasses = computed(() => [
  'tds-scope',
  'tds-form',
  props.lesson && 'tds-form--lesson',
  props.surface && 'teacher-form-surface',
])
</script>

