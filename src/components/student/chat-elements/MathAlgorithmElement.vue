<template>
  <v-card class="glass-card algorithm-card pa-5 mt-2" variant="flat">
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon color="secondary" size="22">mdi-function-variant</v-icon>
      <span class="text-subtitle-1 font-weight-bold">{{ title }}</span>
      <v-chip size="x-small" color="secondary" variant="tonal" class="ms-auto">تجربة تفاعلية</v-chip>
    </div>

    <TransitionGroup name="step-reveal" tag="div" class="steps-list mb-4">
      <div
        v-for="(step, i) in visibleSteps"
        :key="i"
        class="step-row"
        :class="{ 'step-row--result': step.isResult }"
      >
        <span class="step-badge">{{ step.isResult ? '=' : i + 1 }}</span>
        <span class="step-text">{{ step.text }}</span>
      </div>
    </TransitionGroup>

    <v-divider class="mb-4 border-opacity-25" />

    <div class="d-flex align-center gap-2 mb-3">
      <v-icon size="18" color="secondary">mdi-gesture-tap</v-icon>
      <span class="text-body-1 font-weight-bold">جرب بنفسك</span>
    </div>

    <div class="d-flex flex-wrap gap-3">
      <v-text-field
        v-model.number="a"
        type="number"
        label="العدد الأول"
        variant="outlined"
        density="comfortable"
        hide-details
        class="number-input"
        :min="MIN_VALUE"
        :max="MAX_VALUE"
      />
      <v-text-field
        v-model.number="b"
        type="number"
        label="العدد الثاني"
        variant="outlined"
        density="comfortable"
        hide-details
        class="number-input"
        :min="MIN_VALUE"
        :max="MAX_VALUE"
      />
    </div>
  </v-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: 'القاسم المشترك الأكبر' },
  algorithm: { type: String, default: 'gcd' },
  a: { type: Number, default: 48 },
  b: { type: Number, default: 18 },
})

const emit = defineEmits(['reveal'])

const MIN_VALUE = 1
const MAX_VALUE = 100000
const REVEAL_INTERVAL_MS = 450

function clampValue(value) {
  const num = Math.round(Number(value) || MIN_VALUE)
  return Math.min(MAX_VALUE, Math.max(MIN_VALUE, num))
}

const a = ref(clampValue(props.a))
const b = ref(clampValue(props.b))

function computeGcdSteps(rawX, rawY) {
  let x = clampValue(rawX)
  let y = clampValue(rawY)
  const steps = []
  while (y !== 0) {
    const q = Math.floor(x / y)
    const r = x % y
    steps.push({ text: `${x} = ${y} × ${q} + ${r}`, isResult: false })
    x = y
    y = r
  }
  steps.push({ text: `القاسم المشترك الأكبر (GCD) = ${x}`, isResult: true })
  return steps
}

const ALGORITHMS = { gcd: computeGcdSteps }

const steps = computed(() => (ALGORITHMS[props.algorithm] || computeGcdSteps)(a.value, b.value))
const visibleCount = ref(0)
const visibleSteps = computed(() => steps.value.slice(0, visibleCount.value))

let revealTimer = null

function stopReveal() {
  if (revealTimer) {
    clearInterval(revealTimer)
    revealTimer = null
  }
}

function startReveal() {
  stopReveal()
  visibleCount.value = 0
  const total = steps.value.length
  revealTimer = setInterval(() => {
    visibleCount.value += 1
    emit('reveal')
    if (visibleCount.value >= total) stopReveal()
  }, REVEAL_INTERVAL_MS)
}

watch([a, b], ([newA, newB], [oldA, oldB]) => {
  a.value = clampValue(newA)
  b.value = clampValue(newB)
  if (newA === oldA && newB === oldB) return
  stopReveal()
  visibleCount.value = steps.value.length
})

onMounted(() => {
  startReveal()
  emit('reveal')
})

onBeforeUnmount(stopReveal)
</script>

<style scoped>
.algorithm-card {
  border-radius: 16px;
  max-width: 620px;
  border: 1px solid rgba(124, 108, 240, 0.25);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(17, 25, 52, 0.7);
  border: 1px solid var(--em-border, rgba(124, 108, 240, 0.2));
  border-radius: 10px;
  padding: 8px 12px;
  direction: ltr;
}

.step-row--result {
  background: rgba(34, 211, 238, 0.12);
  border-color: rgba(34, 211, 238, 0.4);
}

.step-badge {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(124, 108, 240, 0.2);
  color: #a78bfa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.step-row--result .step-badge {
  background: rgba(34, 211, 238, 0.25);
  color: var(--em-cyan, #22d3ee);
}

.step-text {
  font-weight: 600;
  font-size: 0.95rem;
  color: #fff;
}

.step-row--result .step-text {
  color: var(--em-cyan, #22d3ee);
}

.number-input {
  flex: 1 1 140px;
  max-width: 200px;
}

.step-reveal-enter-active {
  transition: all 0.3s ease;
}

.step-reveal-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
