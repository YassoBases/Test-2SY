<template>
  <div class="radar-wrap">
    <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="radar" role="img" aria-label="Skill strength radar">
      <defs>
        <radialGradient id="radarFill" cx="50%" cy="50%" r="65%">
          <stop offset="0%" stop-color="rgb(var(--v-theme-secondary))" stop-opacity="0.55" />
          <stop offset="100%" stop-color="rgb(var(--v-theme-primary))" stop-opacity="0.12" />
        </radialGradient>
        <filter id="radarGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3.5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- grid rings -->
      <polygon
        v-for="(ring, ri) in rings"
        :key="`r${ri}`"
        :points="ring"
        class="radar-grid"
      />
      <!-- axes -->
      <line
        v-for="(a, ai) in axes"
        :key="`a${ai}`"
        :x1="CENTER" :y1="CENTER" :x2="a.ex" :y2="a.ey"
        class="radar-axis"
      />

      <!-- animated data polygon -->
      <g class="radar-shape" :style="{ '--t': mounted ? 1 : 0 }">
        <polygon :points="dataPoints" class="radar-fill" />
        <circle
          v-for="(p, pi) in dataVerts"
          :key="`v${pi}`"
          :cx="p.x" :cy="p.y" r="4.5"
          class="radar-vert"
          :style="{ animationDelay: `${0.5 + pi * 0.12}s` }"
        />
      </g>

      <!-- labels -->
      <text
        v-for="(a, li) in axes"
        :key="`l${li}`"
        :x="a.lx" :y="a.ly"
        class="radar-label"
        :text-anchor="a.anchor"
      >{{ a.label }} <tspan class="radar-val">{{ a.value }}%</tspan></text>
    </svg>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  // [{ label, value }] — value 0..100
  skills: { type: Array, default: () => [] },
})

const SIZE = 240
const CENTER = SIZE / 2
const R = 76
const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => (mounted.value = true)))

const n = computed(() => Math.max(props.skills.length, 3))

function angleFor(i) {
  return -Math.PI / 2 + (i * 2 * Math.PI) / n.value
}
function pt(i, radius) {
  const a = angleFor(i)
  return { x: CENTER + radius * Math.cos(a), y: CENTER + radius * Math.sin(a) }
}

const rings = computed(() =>
  [0.25, 0.5, 0.75, 1].map((f) =>
    props.skills.map((_, i) => {
      const p = pt(i, R * f)
      return `${p.x},${p.y}`
    }).join(' '),
  ),
)

const axes = computed(() =>
  props.skills.map((s, i) => {
    const e = pt(i, R)
    const l = pt(i, R + 20)
    const anchor = Math.abs(l.x - CENTER) < 6 ? 'middle' : l.x > CENTER ? 'start' : 'end'
    return { ex: e.x, ey: e.y, lx: l.x, ly: l.y + 4, anchor, label: s.label, value: s.value }
  }),
)

const dataVerts = computed(() => props.skills.map((s, i) => pt(i, R * (Math.max(0, Math.min(100, s.value)) / 100))))
const dataPoints = computed(() => dataVerts.value.map((p) => `${p.x},${p.y}`).join(' '))
</script>

<style scoped>
.radar-wrap { display: flex; justify-content: center; }
.radar { width: 100%; max-width: 320px; overflow: visible; }
.radar-grid { fill: none; stroke: rgba(var(--v-theme-on-surface), 0.1); stroke-width: 1; }
.radar-axis { stroke: rgba(var(--v-theme-on-surface), 0.12); stroke-width: 1; }

.radar-shape {
  transform: scale(var(--t, 0)) rotate(calc((1 - var(--t, 0)) * -25deg));
  transform-origin: center;
  opacity: var(--t, 0);
  transition: transform 0.9s cubic-bezier(0.22, 1.2, 0.36, 1), opacity 0.7s ease;
}
.radar-fill {
  fill: url(#radarFill);
  stroke: rgb(var(--v-theme-secondary));
  stroke-width: 2;
  filter: url(#radarGlow);
}
.radar-vert {
  fill: rgb(var(--v-theme-secondary));
  stroke: #fff;
  stroke-width: 1.5;
  animation: vertPulse 2.4s ease-in-out infinite;
}
@keyframes vertPulse {
  0%, 100% { r: 4.2px; opacity: 0.95; }
  50% { r: 6px; opacity: 1; }
}
.radar-label { fill: rgba(var(--v-theme-on-surface), 0.75); font-size: 11px; font-weight: 600; }
.radar-val { fill: rgb(var(--v-theme-secondary)); font-weight: 800; }

@media (prefers-reduced-motion: reduce) {
  .radar-shape { transition: none; }
  .radar-vert { animation: none; }
}
</style>
