<template>
  <div class="wa-voice" :class="{ 'wa-voice--error': !!errorText }">
    <audio
      :key="audioKey"
      ref="audioEl"
      :src="resolvedSrc"
      preload="auto"
      @loadedmetadata="onMeta"
      @durationchange="onMeta"
      @timeupdate="onTime"
      @ended="onEnded"
      @pause="onPause"
      @play="onPlay"
      @error="onAudioError"
      @canplay="onCanPlay"
    />
    <button
      type="button"
      class="wa-voice__play"
      :class="{ 'wa-voice__play--active': playing }"
      :disabled="!!errorText || !resolvedSrc"
      :aria-label="playing ? t('messages.voicePlayer.pause') : t('messages.voicePlayer.play')"
      @click="togglePlay"
    >
      <v-icon size="20">{{ playing ? 'mdi-pause' : 'mdi-play' }}</v-icon>
    </button>
    <div class="wa-voice__body">
      <p v-if="errorText" class="wa-voice__error text-caption mb-1">{{ errorText }}</p>
      <div
        v-else
        class="wa-voice__progress"
        role="slider"
        :aria-valuenow="progressPct"
        @click="onProgressClick"
      >
        <div class="wa-voice__progress-fill" :style="{ width: progressPct + '%' }" />
      </div>
      <div class="wa-voice__footer">
        <span>{{ formatSec(current) }} / {{ formatSec(effectiveDuration) }}</span>
        <div v-if="!errorText" class="d-flex align-center gap-1">
          <button type="button" class="wa-voice__speed" :title="t('messages.voicePlayer.playbackSpeed')" @click="cycleSpeed">
            {{ speedLabel }}
          </button>
          <button type="button" class="wa-voice__replay" :title="t('messages.voicePlayer.replay')" @click="replay">
            <v-icon size="16">mdi-replay</v-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { mediaUrl } from '../../utils/media.js'

const props = defineProps({
  src: { type: String, required: true },
  durationMs: { type: Number, default: null },
  mimeType: { type: String, default: '' },
})

const { t } = useI18n()

const SPEEDS = [1, 1.5, 2]

const audioEl = ref(null)
const playing = ref(false)
const current = ref(0)
const duration = ref(0)
const speedIndex = ref(0)
const errorText = ref('')
const ready = ref(false)
const audioKey = ref(0)

const resolvedSrc = computed(() => mediaUrl(props.src))

const fallbackDurationSec = computed(() => {
  const ms = props.durationMs
  if (ms == null || ms <= 0) return 0
  return ms / 1000
})

const effectiveDuration = computed(() => {
  const d = duration.value
  if (Number.isFinite(d) && d > 0) return d
  return fallbackDurationSec.value
})

const progressPct = computed(() => {
  const total = effectiveDuration.value
  if (!total) return 0
  return Math.min(100, (current.value / total) * 100)
})

const speedLabel = computed(() => `${SPEEDS[speedIndex.value]}×`)

function formatSec(sec) {
  const s = Math.max(0, Math.floor(Number(sec) || 0))
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${m}:${String(r).padStart(2, '0')}`
}

function resetState() {
  playing.value = false
  current.value = 0
  duration.value = 0
  speedIndex.value = 0
  errorText.value = ''
  ready.value = false
}

function reloadAudio() {
  audioKey.value += 1
}

watch(
  () => [props.src, props.durationMs],
  async () => {
    resetState()
    reloadAudio()
    await nextTick()
    const el = audioEl.value
    if (el) {
      try {
        el.load()
      } catch {
        /* ignore */
      }
    }
  },
  { immediate: true },
)

function onMeta() {
  const el = audioEl.value
  if (!el) return
  const d = el.duration
  if (Number.isFinite(d) && d > 0) {
    duration.value = d
    errorText.value = ''
  } else if (fallbackDurationSec.value > 0) {
    duration.value = fallbackDurationSec.value
  }
}

function onCanPlay() {
  ready.value = true
  errorText.value = ''
}

function onTime() {
  current.value = audioEl.value?.currentTime || 0
  if (!duration.value && audioEl.value?.duration) onMeta()
}

function onEnded() {
  playing.value = false
}

function onPlay() {
  playing.value = true
}

function onPause() {
  playing.value = false
}

function onAudioError() {
  playing.value = false
  const mime = (props.mimeType || '').toLowerCase()
  if (mime.includes('webm') && typeof document !== 'undefined') {
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
    if (isSafari) {
      errorText.value = t('messages.voicePlayer.webmUnsupported')
      return
    }
  }
  errorText.value = t('messages.voicePlayer.loadFailed')
}

function applySpeed() {
  const el = audioEl.value
  if (el) el.playbackRate = SPEEDS[speedIndex.value]
}

async function togglePlay() {
  if (errorText.value) return
  const el = audioEl.value
  if (!el) return
  if (playing.value) {
    el.pause()
    return
  }
  applySpeed()
  try {
    if (!ready.value) el.load()
    await el.play()
  } catch {
    errorText.value = t('messages.voicePlayer.playFailed')
  }
}

function onProgressClick(ev) {
  const el = audioEl.value
  const bar = ev.currentTarget
  const total = effectiveDuration.value
  if (!el || !bar || !total) return
  const rect = bar.getBoundingClientRect()
  const ratio = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width))
  const t = ratio * total
  el.currentTime = t
  current.value = t
}

function cycleSpeed() {
  speedIndex.value = (speedIndex.value + 1) % SPEEDS.length
  applySpeed()
  if (playing.value) audioEl.value?.play().catch(() => {})
}

async function replay() {
  if (errorText.value) return
  const el = audioEl.value
  if (!el) return
  el.currentTime = 0
  current.value = 0
  applySpeed()
  try {
    await el.play()
  } catch {
    errorText.value = t('messages.voicePlayer.replayFailed')
  }
}

onUnmounted(() => {
  audioEl.value?.pause()
})
</script>

<style scoped>
.wa-voice--error .wa-voice__play {
  opacity: 0.5;
}
.wa-voice__error {
  color: #fca5a5;
  margin: 0;
  line-height: 1.3;
}
</style>
