import { ref } from 'vue'
import {
  fetchSpeakingConversation,
  fetchSpeakingConversationProgress,
  postSpeakingConversationTurn,
  resetSpeakingConversation,
} from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

const AUDIO_POLL_INTERVAL_MS = 2000
const AUDIO_POLL_MAX_ATTEMPTS = 90

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const VOICE_KEY = 'language_tts_voice'

export function useLanguageConversation() {
  const messages = ref([])
  const effectiveLevel = ref(null)
  const turnCount = ref(0)
  const welcomeHint = ref(null)
  const progress = ref(null)
  const loading = ref(false)
  const processing = ref(false)
  const recording = ref(false)
  const error = ref('')
  const voice = ref(localStorage.getItem(VOICE_KEY) || 'en-US-AriaNeural')
  const focus = ref('')

  function setFocus(f) {
    focus.value = f || ''
  }

  function setVoice(v) {
    voice.value = v
    try {
      localStorage.setItem(VOICE_KEY, v)
    } catch {
      /* ignore storage errors */
    }
  }

  let mediaRecorder = null
  let chunks = []
  let startedAt = 0
  let stream = null

  function applyState(data) {
    messages.value = data.messages || []
    effectiveLevel.value = data.effective_speaking_level
    turnCount.value = data.turn_count || 0
    welcomeHint.value = data.welcome_hint
  }

  function updateAssistantAudio(turnIndex, replyAudioUrl) {
    const idx = messages.value.findIndex(
      (m) => m.role === 'assistant' && m.turn_index === turnIndex,
    )
    if (idx === -1) return
    messages.value[idx] = {
      ...messages.value[idx],
      reply_audio_url: replyAudioUrl,
      reply_audio_pending: false,
    }
  }

  async function pollForReplyAudio(turnIndex) {
    for (let attempt = 0; attempt < AUDIO_POLL_MAX_ATTEMPTS; attempt += 1) {
      await sleep(AUDIO_POLL_INTERVAL_MS)
      try {
        const data = await fetchSpeakingConversation()
        const assistant = (data.messages || []).find(
          (m) => m.role === 'assistant' && m.turn_index === turnIndex,
        )
        if (assistant?.reply_audio_url) {
          updateAssistantAudio(turnIndex, assistant.reply_audio_url)
          return
        }
        if (assistant && !assistant.reply_audio_pending) {
          // Server finished without audio (TTS failed/disabled) — stop the spinner.
          updateAssistantAudio(turnIndex, assistant.reply_audio_url || null)
          return
        }
      } catch {
        /* keep polling */
      }
    }
    // Polling exhausted without audio — clear the pending spinner so it never hangs forever.
    updateAssistantAudio(turnIndex, null)
  }

  async function loadState() {
    loading.value = true
    error.value = ''
    try {
      const data = await fetchSpeakingConversation()
      applyState(data)
    } catch (e) {
      error.value = getErrorMessage(e, 'The conversation could not be loaded')
    } finally {
      loading.value = false
    }
  }

  async function loadProgress() {
    try {
      progress.value = await fetchSpeakingConversationProgress()
      if (progress.value?.effective_speaking_level) {
        effectiveLevel.value = progress.value.effective_speaking_level
      }
    } catch {
      /* optional */
    }
  }

  async function startRecording() {
    error.value = ''
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunks = []
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => onRecordingComplete()
      startedAt = Date.now()
      mediaRecorder.start()
      recording.value = true
    } catch (e) {
      error.value = getErrorMessage(e, 'Unable to access microphone')
    }
  }

  function stopRecording() {
    if (mediaRecorder && recording.value) {
      mediaRecorder.stop()
      recording.value = false
      stream?.getTracks().forEach((t) => t.stop())
    }
  }

  async function submitTurn(blob, duration) {
    if (!blob || !blob.size) {
      error.value = 'The audio is empty — please try again.'
      return
    }
    processing.value = true
    error.value = ''
    try {
      const result = await postSpeakingConversationTurn(blob, duration, voice.value, focus.value)
      messages.value.push({
        role: 'user',
        content: result.transcript,
        turn_index: result.turn_index,
        evaluation: result.evaluation,
      })
      messages.value.push({
        role: 'assistant',
        content: result.reply,
        turn_index: result.turn_index,
        turn_db_id: result.turn_id,
        correction_display: result.correction_display,
        reply_audio_url: result.reply_audio_url,
        reply_audio_pending: result.reply_audio_pending,
        autoplay: true, // only the freshly-generated reply auto-plays (history stays silent)
      })
      turnCount.value = result.turn_index
      effectiveLevel.value = result.effective_speaking_level
      await loadProgress()
      if (result.reply_audio_pending && !result.reply_audio_url) {
        pollForReplyAudio(result.turn_index)
      }
    } catch (e) {
      error.value = getErrorMessage(e, 'Unable to send your audio')
    } finally {
      processing.value = false
    }
  }

  async function onRecordingComplete() {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    const duration = Math.max(1, Math.round((Date.now() - startedAt) / 1000))
    await submitTurn(blob, duration)
  }

  async function uploadAudio(file) {
    if (!file) return
    if (!String(file.type || '').startsWith('audio/')) {
      error.value = 'Please choose an audio file.'
      return
    }
    // Duration is unknown for an uploaded file; it is only used for activity logging.
    await submitTurn(file, null)
  }

  async function resetSession() {
    processing.value = true
    error.value = ''
    try {
      await resetSpeakingConversation()
      messages.value = []
      turnCount.value = 0
      welcomeHint.value = 'Speak in English — I will correct your mistakes and respond to you at a level that suits you.'
      await loadState()
      await loadProgress()
    } catch (e) {
      error.value = getErrorMessage(e, 'Unable to restart the conversation')
    } finally {
      processing.value = false
    }
  }

  return {
    messages,
    effectiveLevel,
    turnCount,
    welcomeHint,
    progress,
    loading,
    processing,
    recording,
    error,
    voice,
    setVoice,
    focus,
    setFocus,
    loadState,
    loadProgress,
    startRecording,
    stopRecording,
    uploadAudio,
    resetSession,
  }
}
