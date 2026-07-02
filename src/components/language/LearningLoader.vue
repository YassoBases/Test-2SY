<template>
  <div class="ll" :class="{ 'll--compact': compact }">
    <div class="ll-orb">
      <v-icon :size="compact ? 24 : 34" color="secondary">{{ icon }}</v-icon>
      <span class="ll-ring"></span>
      <span class="ll-ring ll-ring--2"></span>
    </div>
    <div class="ll-dots">
      <span></span><span></span><span></span>
    </div>
    <h3 v-if="title && !compact" class="text-h6 font-weight-bold mt-3 mb-1">{{ title }}</h3>
    <transition name="ll-tip" mode="out-in">
      <p :key="tip" class="ll-tip text-body-2 text-medium-emphasis mb-0">{{ tip }}</p>
    </transition>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  icon: { type: String, default: 'mdi-brain' },
  compact: { type: Boolean, default: false },
  tips: { type: Array, default: () => [] },
})

const DEFAULT_TIPS = [
  '💡 Saying a word out loud helps you remember it.',
  '💡 Read the questions first — then you know what to look for.',
  '💡 Guessing a word from context builds real fluency.',
  '🎧 Listen for the main idea before the small details.',
  '🌱 A few minutes every day beats one long session.',
  '🗣️ Mistakes are how your brain learns — keep going!',
  '⭐ Re-reading a tricky sentence is a smart move, not a slow one.',
  "🔥 You're building a streak of real progress right now.",
]

const pool = props.tips.length ? props.tips : DEFAULT_TIPS
const tip = ref(pool[Math.floor(Math.random() * pool.length)])
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    let next = tip.value
    while (next === tip.value && pool.length > 1) next = pool[Math.floor(Math.random() * pool.length)]
    tip.value = next
  }, 2800)
})
onUnmounted(() => timer && clearInterval(timer))
</script>

<style scoped>
.ll { text-align: center; padding: 8px 4px; }
.ll-orb {
  position: relative; display: inline-flex; align-items: center; justify-content: center;
  width: 72px; height: 72px; border-radius: 50%;
  background: radial-gradient(circle at 50% 40%, rgba(124, 108, 240, 0.28), rgba(34, 211, 238, 0.08));
  animation: ll-bob 2.4s ease-in-out infinite;
}
.ll--compact .ll-orb { width: 52px; height: 52px; }
.ll-ring {
  position: absolute; inset: 0; border-radius: 50%;
  border: 2px solid rgba(124, 108, 240, 0.5); animation: ll-pulse 2s ease-out infinite;
}
.ll-ring--2 { animation-delay: 1s; border-color: rgba(34, 211, 238, 0.5); }
.ll-dots { display: flex; gap: 6px; justify-content: center; margin-top: 12px; }
.ll-dots span {
  width: 8px; height: 8px; border-radius: 50%; background: rgb(var(--v-theme-secondary));
  animation: ll-jump 1s ease-in-out infinite;
}
.ll-dots span:nth-child(2) { animation-delay: 0.15s; }
.ll-dots span:nth-child(3) { animation-delay: 0.3s; }
.ll-tip { min-height: 1.5em; max-width: 360px; margin-left: auto; margin-right: auto; }
@keyframes ll-bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes ll-pulse { 0% { transform: scale(0.85); opacity: 0.8; } 100% { transform: scale(1.5); opacity: 0; } }
@keyframes ll-jump { 0%, 100% { transform: translateY(0); opacity: 0.6; } 50% { transform: translateY(-7px); opacity: 1; } }
.ll-tip-enter-active, .ll-tip-leave-active { transition: opacity 0.4s ease, transform 0.4s ease; }
.ll-tip-enter-from { opacity: 0; transform: translateY(6px); }
.ll-tip-leave-to { opacity: 0; transform: translateY(-6px); }
@media (prefers-reduced-motion: reduce) {
  .ll-orb, .ll-ring, .ll-dots span { animation: none; }
}
</style>
