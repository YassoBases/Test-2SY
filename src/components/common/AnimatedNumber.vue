<template><span>{{ display }}{{ suffix }}</span></template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: [Number, String], default: 0 },
  duration: { type: Number, default: 900 },
  decimals: { type: Number, default: 0 },
  suffix: { type: String, default: '' },
})

const display = ref(0)
const fmt = (n) => (props.decimals ? Number(n).toFixed(props.decimals) : Math.round(n))

function animate(to) {
  const from = Number(display.value) || 0
  const target = Number(to) || 0
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches || from === target) {
    display.value = fmt(target)
    return
  }
  const start = performance.now()
  function step(now) {
    const t = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - t, 3) // easeOutCubic
    display.value = fmt(from + (target - from) * eased)
    if (t < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(() => animate(props.value))
watch(() => props.value, (v) => animate(v))
</script>
