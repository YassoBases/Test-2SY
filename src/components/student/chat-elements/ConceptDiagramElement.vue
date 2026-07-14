<template>
  <v-card class="glass-card diagram-card pa-5 mt-2" variant="flat">
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon color="secondary" size="22">mdi-graph-outline</v-icon>
      <span class="text-subtitle-1 font-weight-bold">{{ title }}</span>
      <v-chip size="x-small" color="secondary" variant="tonal" class="ms-auto">تجربة تفاعلية</v-chip>
    </div>

    <div v-if="layout === 'radial'" class="radial-stage">
      <svg class="radial-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <line
          v-for="(node, i) in positionedNodes"
          :key="`line-${i}`"
          x1="50"
          y1="50"
          :x2="node.x"
          :y2="node.y"
          class="radial-connector"
          :class="{ 'radial-connector--active': activeIndex === i }"
        />
        <circle cx="50" cy="50" r="6" class="radial-hub" />
      </svg>
      <button
        v-for="(node, i) in positionedNodes"
        :key="i"
        type="button"
        class="radial-node"
        :class="{ 'radial-node--active': activeIndex === i }"
        :style="{ left: node.x + '%', top: node.y + '%' }"
        @click="toggleActive(i)"
      >
        <span class="node-label">{{ node.label }}</span>
        <span class="node-desc">{{ node.description }}</span>
      </button>
    </div>

    <TransitionGroup v-else name="node-reveal" tag="div" class="sequence-stage">
      <button
        v-for="(node, i) in visibleNodes"
        :key="i"
        type="button"
        class="sequence-node"
        :class="{ 'sequence-node--active': activeIndex === i }"
        @click="toggleActive(i)"
      >
        <span class="sequence-badge">{{ i + 1 }}</span>
        <span class="node-label">{{ node.label }}</span>
        <span v-if="node.date" class="sequence-date">{{ node.date }}</span>
        <span class="node-desc">{{ node.description }}</span>
      </button>
    </TransitionGroup>
  </v-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  layout: { type: String, default: 'sequence' },
  nodes: { type: Array, default: () => [] },
})

const emit = defineEmits(['reveal'])

const REVEAL_INTERVAL_MS = 400

const activeIndex = ref(null)

function toggleActive(i) {
  activeIndex.value = activeIndex.value === i ? null : i
}

const positionedNodes = computed(() => {
  const n = props.nodes.length || 1
  const radius = 38
  return props.nodes.map((node, i) => {
    const angle = -Math.PI / 2 + i * ((2 * Math.PI) / n)
    return {
      ...node,
      x: 50 + radius * Math.cos(angle),
      y: 50 + radius * Math.sin(angle),
    }
  })
})

const visibleCount = ref(props.layout === 'radial' ? props.nodes.length : 0)
const visibleNodes = computed(() => props.nodes.slice(0, visibleCount.value))

let revealTimer = null

function stopReveal() {
  if (revealTimer) {
    clearInterval(revealTimer)
    revealTimer = null
  }
}

onMounted(() => {
  if (props.layout !== 'sequence') {
    emit('reveal')
    return
  }
  const total = props.nodes.length
  revealTimer = setInterval(() => {
    visibleCount.value += 1
    emit('reveal')
    if (visibleCount.value >= total) stopReveal()
  }, REVEAL_INTERVAL_MS)
})

onBeforeUnmount(stopReveal)
</script>

<style scoped>
.diagram-card {
  border-radius: 16px;
  max-width: 760px;
  border: 1px solid rgba(124, 108, 240, 0.25);
}

.radial-stage {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  max-height: 460px;
  margin: 0 auto;
}

.radial-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.radial-connector {
  stroke: rgba(34, 211, 238, 0.25);
  stroke-width: 0.6;
}

.radial-connector--active {
  stroke: var(--em-cyan, #22d3ee);
  stroke-width: 1;
}

.radial-hub {
  fill: #7c6cf0;
  filter: drop-shadow(0 0 6px rgba(124, 108, 240, 0.65));
}

.radial-node {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 150px;
  max-width: 40%;
  background: rgba(17, 25, 52, 0.92);
  border: 1px solid rgba(124, 108, 240, 0.3);
  border-radius: 12px;
  padding: 8px 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.radial-node:hover,
.radial-node--active {
  border-color: var(--em-cyan, #22d3ee);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.25);
}

.sequence-stage {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.sequence-node {
  flex: 1 1 160px;
  max-width: 220px;
  background: rgba(17, 25, 52, 0.92);
  border: 1px solid rgba(124, 108, 240, 0.3);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: start;
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.sequence-node:hover,
.sequence-node--active {
  border-color: var(--em-cyan, #22d3ee);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.25);
}

.sequence-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(34, 211, 238, 0.15);
  color: var(--em-cyan, #22d3ee);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.sequence-date {
  font-size: 0.7rem;
  color: var(--em-cyan, #22d3ee);
  font-weight: 600;
}

.node-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
}

.node-desc {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.4;
}

.node-reveal-enter-active {
  transition: all 0.3s ease;
}

.node-reveal-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
