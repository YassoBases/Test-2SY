<template>
  <div class="viz">
    <canvas ref="canvasEl" class="viz-canvas" aria-hidden="true" />
    <audio ref="audioEl" :src="src" controls class="w-100 viz-audio" @play="onPlay" @error="$emit('error')" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref } from 'vue'

const props = defineProps({ src: { type: String, default: '' } })
defineEmits(['error'])

const audioEl = ref(null)
const canvasEl = ref(null)
let ctx = null
let analyser = null
let raf = null
let data = null

const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches

function setup() {
  if (ctx || !audioEl.value) return
  const AC = window.AudioContext || window.webkitAudioContext
  if (!AC) return
  ctx = new AC()
  const source = ctx.createMediaElementSource(audioEl.value)
  analyser = ctx.createAnalyser()
  analyser.fftSize = 128
  analyser.smoothingTimeConstant = 0.8
  source.connect(analyser)
  analyser.connect(ctx.destination)
  data = new Uint8Array(analyser.frequencyBinCount)
}

function draw() {
  const c = canvasEl.value
  if (!c || !analyser) return
  const dpr = window.devicePixelRatio || 1
  const w = (c.width = c.clientWidth * dpr)
  const h = (c.height = c.clientHeight * dpr)
  const g = c.getContext('2d')
  analyser.getByteFrequencyData(data)
  g.clearRect(0, 0, w, h)
  const n = data.length
  const bw = w / n
  for (let i = 0; i < n; i++) {
    const v = data[i] / 255
    const bh = Math.max(2 * dpr, v * h)
    const grd = g.createLinearGradient(0, h, 0, h - bh)
    grd.addColorStop(0, '#22d3ee')
    grd.addColorStop(1, '#a78bfa')
    g.fillStyle = grd
    g.fillRect(i * bw + bw * 0.18, h - bh, bw * 0.64, bh)
  }
  raf = requestAnimationFrame(draw)
}

async function onPlay() {
  if (reduced()) return
  setup()
  if (ctx?.state === 'suspended') await ctx.resume()
  if (!raf) draw()
}

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf)
  ctx?.close?.()
})
</script>

<style scoped>
.viz { position: relative; }
.viz-canvas {
  width: 100%;
  height: 56px;
  display: block;
  margin-bottom: 8px;
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.06), rgba(167, 139, 250, 0.04));
}
.viz-audio { display: block; }
</style>
