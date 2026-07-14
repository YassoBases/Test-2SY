import { computed, onUnmounted, ref } from 'vue'

const BAR_COUNT = 16

export function useVoiceRecorder({ minSeconds = 60, maxSeconds = null } = {}) {
  const recording = ref(false)
  const elapsed = ref(0)
  const ready = ref(false)
  const audioBlob = ref(null)
  const barHeights = ref(Array(BAR_COUNT).fill(10))

  let tickTimer = null
  let waveTimer = null
  let mediaRecorder = null
  let mediaStream = null
  let chunks = []

  const meetsMinimum = computed(() => elapsed.value >= minSeconds)

  const formattedTime = computed(() => {
    const m = Math.floor(elapsed.value / 60)
    const s = elapsed.value % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })

  const progressPercent = computed(() => {
    if (maxSeconds) return Math.min(100, (elapsed.value / maxSeconds) * 100)
    return Math.min(100, (elapsed.value / minSeconds) * 100)
  })

  const remainingSeconds = computed(() => {
    if (maxSeconds) return Math.max(0, maxSeconds - elapsed.value)
    return Math.max(0, minSeconds - elapsed.value)
  })

  function animateWaveform() {
    waveTimer = setInterval(() => {
      barHeights.value = barHeights.value.map(() => 8 + Math.random() * 44)
    }, 90)
  }

  function stopWaveform() {
    if (waveTimer) {
      clearInterval(waveTimer)
      waveTimer = null
    }
    barHeights.value = Array(BAR_COUNT).fill(10)
  }

  function cleanupStream() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop())
      mediaStream = null
    }
  }

  async function startRecording() {
    reset(false)
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      throw new Error('تعذر الوصول للميكروفون')
    }

    chunks = []
    mediaRecorder = new MediaRecorder(mediaStream)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      if (chunks.length) {
        audioBlob.value = new Blob(chunks, { type: mediaRecorder.mimeType || 'audio/webm' })
      }
      cleanupStream()
      ready.value = meetsMinimum.value && !!audioBlob.value
    }
    mediaRecorder.start()

    elapsed.value = 0
    recording.value = true
    animateWaveform()

    tickTimer = setInterval(() => {
      elapsed.value += 1
      if (maxSeconds && elapsed.value >= maxSeconds) stopRecording()
    }, 1000)
  }

  function stopRecording() {
    recording.value = false
    stopWaveform()
    if (tickTimer) {
      clearInterval(tickTimer)
      tickTimer = null
    }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    } else {
      cleanupStream()
      ready.value = meetsMinimum.value
    }
  }

  function toggleRecording() {
    if (recording.value) stopRecording()
    else startRecording()
  }

  function setBlob(blob) {
    audioBlob.value = blob
    ready.value = !!blob
  }

  function reset(clearElapsed = true) {
    if (recording.value) stopRecording()
    if (clearElapsed) elapsed.value = 0
    ready.value = false
    audioBlob.value = null
    chunks = []
  }

  onUnmounted(() => {
    if (tickTimer) clearInterval(tickTimer)
    stopWaveform()
    cleanupStream()
  })

  return {
    recording,
    elapsed,
    ready,
    audioBlob,
    barHeights,
    barCount: BAR_COUNT,
    formattedTime,
    progressPercent,
    remainingSeconds,
    minSeconds,
    maxSeconds,
    meetsMinimum,
    toggleRecording,
    startRecording,
    stopRecording,
    setBlob,
    reset,
  }
}
