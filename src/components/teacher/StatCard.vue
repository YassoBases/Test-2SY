<template>
  <v-card
    class="stat-card glass-card eduspark-card-hover pa-5 pa-md-6"
    :class="`stat-card--${colorKey}`"
    variant="flat"
  >
    <span class="stat-card__accent" aria-hidden="true" />
    <div class="d-flex align-start justify-space-between gap-3">
      <div class="flex-grow-1 min-w-0">
        <div class="text-caption text-medium-emphasis mb-2">{{ stat.title }}</div>
        <div class="text-h4 font-weight-bold mb-1">{{ stat.value }}</div>
        <div
          v-if="trendText"
          class="text-caption d-flex align-center gap-1"
          :class="trendClass"
        >
          <v-icon size="14">{{ trendIcon }}</v-icon>
          <span>{{ trendText }}</span>
        </div>
        <v-progress-linear
          v-if="hasProgress"
          class="stat-card__progress progress-glow rounded-pill"
          :model-value="progressValue"
          height="6"
          :color="colorKey"
          rounded
        />
      </div>
      <v-avatar
        size="56"
        rounded="xl"
        class="stat-icon flex-shrink-0"
        :class="`stat-icon--${colorKey}`"
        :style="{ '--glow': glowColor }"
      >
        <v-icon :icon="stat.icon || 'mdi-chart-line'" size="28" :color="colorKey" />
      </v-avatar>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stat: { type: Object, required: true },
})

const glowMap = {
  primary: 'rgba(124, 108, 240, 0.4)',
  secondary: 'rgba(34, 211, 238, 0.4)',
  accent: 'rgba(167, 139, 250, 0.4)',
  success: 'rgba(52, 211, 153, 0.4)',
  warning: 'rgba(251, 191, 36, 0.4)',
  error: 'rgba(248, 113, 113, 0.4)',
  info: 'rgba(56, 189, 248, 0.4)',
}

const colorKey = computed(() => props.stat.color || 'primary')
const glowColor = computed(() => glowMap[colorKey.value] ?? glowMap.primary)

const trendText = computed(() => props.stat.trend || props.stat.subtitle || '')
const trendDirection = computed(() => props.stat.trendDirection || props.stat.trend_direction || 'neutral')

const trendClass = computed(() => {
  const map = {
    up: 'text-success',
    down: 'text-error',
    warning: 'text-warning',
    neutral: 'text-medium-emphasis',
  }
  return map[trendDirection.value] || map.neutral
})

const trendIcon = computed(() => {
  const map = {
    up: 'mdi-trending-up',
    down: 'mdi-trending-down',
    warning: 'mdi-alert-circle-outline',
    neutral: 'mdi-minus',
  }
  return map[trendDirection.value] || map.neutral
})

const progressValue = computed(() => {
  const p = props.stat.percent ?? props.stat.progress
  if (p == null || p === '') return null
  const n = Number(p)
  if (Number.isNaN(n)) return null
  return Math.min(100, Math.max(0, n))
})

const hasProgress = computed(() => progressValue.value != null)
</script>

<style scoped>
.stat-icon {
  background: rgba(124, 108, 240, 0.12) !important;
  border: 1px solid var(--em-border);
  box-shadow: 0 0 24px var(--glow);
}

.stat-icon--secondary {
  background: rgba(34, 211, 238, 0.1) !important;
}

.stat-icon--success {
  background: rgba(52, 211, 153, 0.1) !important;
}

.stat-icon--warning {
  background: rgba(251, 191, 36, 0.1) !important;
}

.stat-icon--error {
  background: rgba(248, 113, 113, 0.1) !important;
}
</style>
