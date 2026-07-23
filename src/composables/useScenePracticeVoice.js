import { onBeforeUnmount, ref } from 'vue'
import { extensionForMime, getPreferredRecorderMime } from '../utils/voiceRecording.js'

/**
 * Reusable Speaking voice client (mic + playback).
 *
 * Owns ONLY: mic permission, MediaRecorder capture, playback, ephemeral UI mode.
 * Owns NEVER: dialogue, corrections, progression, evaluation, transcript.
 * Discussion (or any caller) supplies respondFn and owns Claude tutoring.
 *
 * Flow: record → respond(fn) → play optional audio → wait for next recording.
 */
export function useScenePracticeVoice() {
  // idle | priming | listening | recording | thinking | partner_speaking | fallback
  const mode = ref('idle')
  const error = ref('')
  const lastHeard = ref('')
  const lastDecision = ref(null)
  const lastCorrection = ref(null)

  let mediaStream = null
  let mediaRecorder = null
  let chunks = []
  let playbackAudio = null
  let mimeType = 'audio/webm'

  function clearEphemeral() {
    lastHeard.value = ''
    lastDecision.value = null
    lastCorrection.value = null
  }

  function stopPlayback() {
    if (playbackAudio) {
      try {
        playbackAudio.pause()
        playbackAudio.src = ''
      } catch {
        /* noop */
      }
      playbackAudio = null
    }
  }

  function releaseMic() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try {
        mediaRecorder.stop()
      } catch {
        /* noop */
      }
    }
    mediaRecorder = null
    chunks = []
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop())
      mediaStream = null
    }
  }

  function stop() {
    stopPlayback()
    releaseMic()
    if (mode.value !== 'fallback') mode.value = 'idle'
  }

  async function playAudioB64(b64, mime) {
    if (!b64) return false
    stopPlayback()
    try {
      const binary = atob(b64)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i)
      const blob = new Blob([bytes], { type: mime || 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      playbackAudio = new Audio(url)
      const previous = mode.value === 'partner_speaking' ? 'listening' : mode.value
      mode.value = 'partner_speaking'
      await new Promise((resolve) => {
        playbackAudio.onended = () => {
          URL.revokeObjectURL(url)
          resolve()
        }
        playbackAudio.onerror = () => {
          URL.revokeObjectURL(url)
          resolve()
        }
        playbackAudio.play().catch(() => resolve())
      })
      if (mode.value === 'partner_speaking') {
        mode.value = previous === 'fallback' ? 'fallback' : 'listening'
      }
      return true
    } catch {
      if (mode.value === 'partner_speaking') mode.value = 'listening'
      return false
    }
  }

  /**
   * Prime mic permission when entering Live Voice Discussion.
   * Falls back to typed mode when mic/MediaRecorder is unavailable.
   */
  async function prime() {
    if (mode.value === 'listening' || mode.value === 'recording' || mode.value === 'thinking') {
      return mode.value !== 'fallback'
    }
    error.value = ''
    mode.value = 'priming'
    if (!navigator?.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      mode.value = 'fallback'
      return false
    }
    try {
      mimeType = getPreferredRecorderMime() || 'audio/webm'
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Keep the stream warm so the first record click has no permission delay.
      mode.value = 'listening'
      return true
    } catch {
      releaseMic()
      mode.value = 'fallback'
      return false
    }
  }

  async function ensureStream() {
    if (mediaStream && mediaStream.getTracks().some((t) => t.readyState === 'live')) {
      return true
    }
    return prime()
  }

  async function startRecording() {
    if (mode.value === 'fallback' || mode.value === 'thinking' || mode.value === 'partner_speaking') {
      return false
    }
    error.value = ''
    stopPlayback()
    const ok = await ensureStream()
    if (!ok || !mediaStream) {
      mode.value = 'fallback'
      return false
    }
    chunks = []
    try {
      mediaRecorder = mimeType
        ? new MediaRecorder(mediaStream, { mimeType })
        : new MediaRecorder(mediaStream)
    } catch {
      mediaRecorder = new MediaRecorder(mediaStream)
    }
    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) chunks.push(event.data)
    }
    mediaRecorder.start()
    mode.value = 'recording'
    return true
  }

  /**
   * Stop recording and hand the blob to `respondFn`.
   * `respondFn` should return `{ student_transcript?, audio_b64?, audio_mime?, ... }`.
   */
  async function stopRecordingAndRespond(respondFn) {
    if (mode.value !== 'recording' || !mediaRecorder) {
      return null
    }
    const blob = await new Promise((resolve) => {
      mediaRecorder.onstop = () => {
        const type = mediaRecorder?.mimeType || mimeType || 'audio/webm'
        resolve(chunks.length ? new Blob(chunks, { type }) : null)
      }
      try {
        mediaRecorder.stop()
      } catch {
        resolve(null)
      }
    })
    mediaRecorder = null
    chunks = []

    if (!blob || blob.size < 400) {
      mode.value = 'listening'
      error.value = ''
      return null
    }

    mode.value = 'thinking'
    try {
      const result = await respondFn(blob, {
        filename: `discussion_turn${extensionForMime(blob.type || mimeType)}`,
      })
      lastHeard.value = result?.student_transcript || ''
      lastDecision.value = result?.decision ?? result?.latest_assistant?.can_advance ?? null
      const corr = result?.latest_assistant?.correction || result?.micro_correction || null
      lastCorrection.value = corr

      // Audio failure must never fail the turn — text is enough.
      if (result?.audio_b64) {
        await playAudioB64(result.audio_b64, result.audio_mime)
      }
      mode.value = result?.state?.completed ? 'idle' : 'listening'
      return result
    } catch (err) {
      console.warn('[SpeakingVoice] respond failed', err)
      mode.value = 'listening'
      throw err
    }
  }

  /** Play tutor audio returned from open/advance (no recording). */
  async function playTutorAudio(b64, mime) {
    if (!b64) return false
    return playAudioB64(b64, mime)
  }

  function isVoiceActive() {
    return ['priming', 'listening', 'recording', 'thinking', 'partner_speaking'].includes(mode.value)
  }

  onBeforeUnmount(stop)

  return {
    mode,
    error,
    lastHeard,
    lastDecision,
    lastCorrection,
    prime,
    startRecording,
    stopRecordingAndRespond,
    playTutorAudio,
    stop,
    isVoiceActive,
    clearEphemeral,
  }
}
