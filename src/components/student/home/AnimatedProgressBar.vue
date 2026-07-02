<template>
  <v-progress-linear
    :model-value="displayValue"
    :color="color"
    :height="height"
    :rounded="rounded"
    :class="['animated-progress', { 'animated-progress--ready': ready }]"
  />
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  color: { type: String, default: 'primary' },
  height: { type: [Number, String], default: 8 },
  rounded: { type: Boolean, default: true },
  delay: { type: Number, default: 120 },
})

const displayValue = ref(0)
const ready = ref(false)

function animateTo(target) {
  ready.value = false
  displayValue.value = 0
  window.setTimeout(() => {
    displayValue.value = Math.min(100, Math.max(0, target || 0))
    ready.value = true
  }, props.delay)
}

onMounted(() => animateTo(props.value))
watch(() => props.value, animateTo)
</script>

<style scoped>
.animated-progress :deep(.v-progress-linear__determinate) {
  transition: width 1s var(--em-ease-spring);
}

.animated-progress:not(.animated-progress--ready) :deep(.v-progress-linear__determinate) {
  width: 0 !important;
}
</style>
