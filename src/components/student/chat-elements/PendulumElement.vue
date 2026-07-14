<template>
  <v-card class="glass-card pendulum-card pa-5 mt-2" variant="flat">
    <div class="d-flex align-center gap-2 mb-1">
      <v-icon color="secondary" size="22">mdi-pendulum</v-icon>
      <span class="text-subtitle-1 font-weight-bold">محاكاة النواس</span>
      <v-chip size="x-small" color="secondary" variant="tonal" class="ms-auto">تجربة تفاعلية</v-chip>
    </div>

    <p v-if="caption" class="text-body-2 text-medium-emphasis mb-3">{{ caption }}</p>

    <div class="pendulum-stage">
      <svg viewBox="0 0 680 360" class="pendulum-svg">
        <defs>
          <radialGradient id="bobGradient" cx="35%" cy="30%" r="65%">
            <stop offset="0%" stop-color="#a78bfa" />
            <stop offset="100%" stop-color="#5b4fcf" />
          </radialGradient>
        </defs>

        <rect x="254" y="20" width="173" height="14" rx="6" class="pendulum-mount" />
        <line
          v-for="i in 5"
          :key="i"
          :x1="266 + i * 29"
          y1="35"
          :x2="251 + i * 29"
          y2="52"
          class="pendulum-hatch"
        />

        <line :x1="pivotX" :y1="pivotY" :x2="leftGuideX" :y2="leftGuideY" class="pendulum-arc-guide" />
        <line :x1="pivotX" :y1="pivotY" :x2="rightGuideX" :y2="rightGuideY" class="pendulum-arc-guide" />

        <line :x1="pivotX" :y1="pivotY" :x2="bobX" :y2="bobY" class="pendulum-arm" />
        <circle :cx="pivotX" :cy="pivotY" r="9" class="pendulum-pivot" />
        <circle :cx="bobX" :cy="bobY" r="26" fill="url(#bobGradient)" class="pendulum-bob" />
      </svg>
    </div>

    <div class="control-label d-flex justify-space-between align-center mb-1">
      <span class="text-body-2 font-weight-medium">طول النواس</span>
      <span class="value-badge">{{ length.toFixed(1) }} م</span>
    </div>
    <v-slider
      v-model="length"
      :min="MIN_LENGTH"
      :max="MAX_LENGTH"
      :step="0.1"
      color="secondary"
      hide-details
      class="mb-3"
    />

    <div class="period-display d-flex align-center justify-center gap-2">
      <v-icon size="18" color="secondary">mdi-clock-outline</v-icon>
      <span class="text-body-1 font-weight-bold">الزمن الدوري: {{ periodSeconds.toFixed(2) }} ثانية</span>
    </div>
  </v-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  caption: { type: String, default: '' },
  lengthM: { type: Number, default: 1.0 },
})

const emit = defineEmits(['reveal'])

const MIN_LENGTH = 0.2
const MAX_LENGTH = 2.0
const GRAVITY = 9.8
const MAX_ANGLE_RAD = (25 * Math.PI) / 180
const PIXELS_PER_METER = 138

const PIVOT_X = 340
const PIVOT_Y = 44

const length = ref(Math.min(MAX_LENGTH, Math.max(MIN_LENGTH, props.lengthM || 1.0)))
const time = ref(0)

const periodSeconds = computed(() => 2 * Math.PI * Math.sqrt(length.value / GRAVITY))
const angularFrequency = computed(() => Math.sqrt(GRAVITY / length.value))
const currentAngle = computed(() => MAX_ANGLE_RAD * Math.cos(angularFrequency.value * time.value))

const pivotX = PIVOT_X
const pivotY = PIVOT_Y
const armLengthPx = computed(() => length.value * PIXELS_PER_METER)
const bobX = computed(() => pivotX + armLengthPx.value * Math.sin(currentAngle.value))
const bobY = computed(() => pivotY + armLengthPx.value * Math.cos(currentAngle.value))

const leftGuideX = computed(() => pivotX - armLengthPx.value * Math.sin(MAX_ANGLE_RAD))
const leftGuideY = computed(() => pivotY + armLengthPx.value * Math.cos(MAX_ANGLE_RAD))
const rightGuideX = computed(() => pivotX + armLengthPx.value * Math.sin(MAX_ANGLE_RAD))
const rightGuideY = computed(() => leftGuideY.value)

let frameId = null
let lastTimestamp = null

function tick(timestamp) {
  if (lastTimestamp !== null) {
    time.value += (timestamp - lastTimestamp) / 1000
  }
  lastTimestamp = timestamp
  frameId = requestAnimationFrame(tick)
}

onMounted(() => {
  frameId = requestAnimationFrame(tick)
  emit('reveal')
})

onBeforeUnmount(() => {
  if (frameId) cancelAnimationFrame(frameId)
})
</script>

<style scoped>
.pendulum-card {
  border-radius: 16px;
  max-width: 760px;
  border: 1px solid rgba(124, 108, 240, 0.25);
}

.pendulum-stage {
  display: flex;
  justify-content: center;
  background: radial-gradient(circle at 50% 20%, rgba(124, 108, 240, 0.08), transparent 70%);
  border-radius: 12px;
  padding: 4px 0 0;
}

.pendulum-svg {
  width: 100%;
  max-width: 680px;
  height: 340px;
}

.pendulum-mount {
  fill: rgba(255, 255, 255, 0.18);
}

.pendulum-hatch {
  stroke: rgba(255, 255, 255, 0.18);
  stroke-width: 2;
}

.pendulum-arc-guide {
  stroke: rgba(34, 211, 238, 0.22);
  stroke-width: 2;
  stroke-dasharray: 5 5;
}

.pendulum-arm {
  stroke: var(--em-cyan, #22d3ee);
  stroke-width: 4;
  stroke-linecap: round;
}

.pendulum-pivot {
  fill: rgba(255, 255, 255, 0.75);
}

.pendulum-bob {
  filter: drop-shadow(0 0 10px rgba(124, 108, 240, 0.65));
}

.value-badge {
  background: rgba(34, 211, 238, 0.12);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: 8px;
  padding: 2px 10px;
  font-weight: 700;
  color: var(--em-cyan, #22d3ee);
  font-size: 0.85rem;
}

.period-display {
  background: rgba(124, 108, 240, 0.1);
  border: 1px solid rgba(124, 108, 240, 0.3);
  border-radius: 10px;
  padding: 10px 14px;
}
</style>
