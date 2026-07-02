<template>
  <div class="insight-floats" aria-hidden="true">
    <div
      v-for="(chip, i) in chips"
      :key="chip.text"
      class="insight-chip glass-card"
      :style="chipStyle(i)"
    >
      <v-icon size="14" color="secondary" class="insight-chip__icon">mdi-shimmer</v-icon>
      <span>{{ chip.text }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { tm } = useI18n()

const chips = computed(() => tm('auth.welcome.insights').map((text) => ({ text })))

function chipStyle(i) {
  const positions = [
    { top: '4%', left: '8%', animationDuration: '14s' },
    { top: '38%', left: '2%', animationDuration: '17s' },
    { top: '62%', left: '18%', animationDuration: '12s' },
  ]
  const p = positions[i] || positions[0]
  return {
    ...p,
    animationDelay: `${i * -3}s`,
  }
}
</script>

<style scoped>
.insight-floats {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.insight-chip {
  position: absolute;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  font-size: clamp(0.58rem, 1vh, 0.65rem);
  color: rgba(232, 236, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.06) !important;
  background: rgba(12, 18, 40, 0.35) !important;
  backdrop-filter: blur(10px);
  border-radius: 10px;
  white-space: nowrap;
  animation: insight-drift ease-in-out infinite;
  opacity: 0.45;
}

.insight-chip__icon {
  opacity: 0.7;
}

@keyframes insight-drift {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0.35;
  }
  50% {
    transform: translateY(-10px) translateX(6px);
    opacity: 0.55;
  }
}
</style>
