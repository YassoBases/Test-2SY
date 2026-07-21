import { computed, ref } from 'vue'
import {
  advanceSpeakingDiscussion,
  fetchActiveSpeakingDiscussion,
  openSpeakingDiscussion,
  submitSpeakingDiscussion,
  submitSpeakingDiscussionVoice,
} from '../api/speakingDiscussion.js'

function apply(target, data) {
  target.value = data || null
}

function errorDetail(err, fallback) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (detail && typeof detail === 'object') {
    if (typeof detail.message === 'string' && detail.message.trim()) return detail.message
    if (typeof detail.msg === 'string' && detail.msg.trim()) return detail.msg
  }
  return err?.message || fallback
}

export function useSpeakingDiscussion() {
  const view = ref(null)
  const loading = ref(false)
  const submitting = ref(false)
  const advancing = ref(false)
  const error = ref('')
  const draft = ref('')
  const lastAudio = ref(null)

  const state = computed(() => view.value?.state || null)
  const currentStep = computed(() => view.value?.current_step || null)
  const turns = computed(() => state.value?.turns || [])
  const phase = computed(() => state.value?.phase || '')
  const completed = computed(() => Boolean(state.value?.completed))
  const readyForAlex = computed(() => Boolean(state.value?.ready_for_alex))
  const latestAssistant = computed(() => view.value?.latest_assistant || null)
  const stepsTotal = computed(() => view.value?.steps_total || 0)
  const stepIndex = computed(() => state.value?.step_index ?? 0)
  const packageTitle = computed(() => view.value?.package_title || '')
  const packageSnippet = computed(() => view.value?.package_snippet || {})
  const canAdvance = computed(() => {
    if (completed.value) return false
    const la = latestAssistant.value
    if (la?.can_advance) return true
    return phase.value === 'next_question'
  })
  const progressPercent = computed(() => {
    const total = stepsTotal.value || 1
    const done = completed.value ? total : stepIndex.value
    return Math.min(100, Math.round((100 * done) / total))
  })

  function captureAudio(data) {
    if (data?.audio_b64) {
      lastAudio.value = { b64: data.audio_b64, mime: data.audio_mime || 'audio/wav' }
    } else {
      lastAudio.value = null
    }
    return data
  }

  async function openDiscussion({ packageId, forceRestart } = {}) {
    loading.value = true
    error.value = ''
    try {
      const data = captureAudio(await openSpeakingDiscussion({ packageId, forceRestart }))
      apply(view, data)
      draft.value = ''
      return data
    } catch (err) {
      error.value = errorDetail(err, 'Failed to open discussion')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadActive() {
    loading.value = true
    error.value = ''
    try {
      const data = captureAudio(await fetchActiveSpeakingDiscussion())
      apply(view, data)
      return data
    } catch (err) {
      if (err?.response?.status === 404) {
        view.value = null
        error.value = ''
        lastAudio.value = null
        return null
      }
      error.value = errorDetail(err, 'Failed to load discussion')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function submit() {
    const text = draft.value.trim()
    if (!text) return
    submitting.value = true
    error.value = ''
    try {
      const data = captureAudio(await submitSpeakingDiscussion(text))
      apply(view, data)
      draft.value = ''
      return data
    } catch (err) {
      error.value = errorDetail(err, 'Failed to submit')
      throw err
    } finally {
      submitting.value = false
    }
  }

  async function submitVoice(blob, meta = {}) {
    if (!blob) return null
    submitting.value = true
    error.value = ''
    try {
      const data = captureAudio(await submitSpeakingDiscussionVoice(blob, meta))
      apply(view, data)
      draft.value = ''
      return data
    } catch (err) {
      error.value = errorDetail(err, 'Failed to submit voice')
      throw err
    } finally {
      submitting.value = false
    }
  }

  async function advance() {
    advancing.value = true
    error.value = ''
    try {
      const data = captureAudio(await advanceSpeakingDiscussion())
      apply(view, data)
      return data
    } catch (err) {
      error.value = errorDetail(err, 'Failed to advance')
      throw err
    } finally {
      advancing.value = false
    }
  }

  return {
    view,
    loading,
    submitting,
    advancing,
    error,
    draft,
    lastAudio,
    state,
    currentStep,
    turns,
    phase,
    completed,
    readyForAlex,
    latestAssistant,
    stepsTotal,
    stepIndex,
    packageTitle,
    packageSnippet,
    canAdvance,
    progressPercent,
    openDiscussion,
    loadActive,
    submit,
    submitVoice,
    advance,
  }
}
