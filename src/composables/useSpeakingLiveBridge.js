import { computed, ref } from 'vue'
import {
  completeSpeakingRehearsal,
  fetchActiveLiveBridge,
  prepareSpeakingLiveBridge,
  respondSpeakingRehearsal,
  startSpeakingRehearsal,
  submitSpeakingRehearsalTurn,
} from '../api/speakingLiveBridge.js'

function studentSafeMessage(err, fallback) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (detail?.message) return String(detail.message)
  return fallback
}

/** Usable bridge payload — bare idle shell from GET /active is not hydrated. */
export function isBridgeHydrated(raw) {
  if (!raw || typeof raw !== 'object') return false
  const phase = String(raw.journey_phase || 'idle')
  if (phase !== 'idle') return true
  if (raw.preparation || raw.rehearsal || raw.live_context || raw.ready_for_live) return true
  return false
}

export function useSpeakingLiveBridge() {
  const loading = ref(false)
  const busy = ref(false)
  const error = ref('')
  const bridge = ref(null)
  const draft = ref('')

  let hydrateInFlight = null

  const journeyPhase = computed(() => bridge.value?.journey_phase || 'idle')
  const preparation = computed(() => bridge.value?.preparation || null)
  const rehearsal = computed(() => bridge.value?.rehearsal || null)
  const voiceSession = computed(() => bridge.value?.voice_session || null)
  const liveContext = computed(() => bridge.value?.live_context || null)
  const readyForLive = computed(() => Boolean(bridge.value?.ready_for_live))
  const turns = computed(() => rehearsal.value?.turns || [])
  const hydrated = computed(() => isBridgeHydrated(bridge.value))

  function clearError() {
    error.value = ''
  }

  function apply(raw) {
    bridge.value = raw || null
    return bridge.value
  }

  async function loadBridge() {
    loading.value = true
    clearError()
    try {
      apply(await fetchActiveLiveBridge())
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to load your scene')
    } finally {
      loading.value = false
    }
  }

  /** Hydrated AND, when the caller knows the current case, for the same package. */
  function isUsableFor(raw, packageId) {
    if (!isBridgeHydrated(raw)) return false
    if (packageId && raw.package_id && String(raw.package_id) !== String(packageId)) return false
    return true
  }

  /**
   * Bridge owns hydration. Safe to call on every Bridge entry / refresh.
   * GET /active → if usable for the current case, keep it; else POST /prepare.
   */
  async function ensureHydrated({ packageId } = {}) {
    if (isUsableFor(bridge.value, packageId)) return bridge.value
    if (hydrateInFlight) return hydrateInFlight

    hydrateInFlight = (async () => {
      loading.value = true
      clearError()
      try {
        try {
          apply(await fetchActiveLiveBridge())
        } catch {
          /* fall through to prepare */
        }

        if (!isUsableFor(bridge.value, packageId)) {
          apply(await prepareSpeakingLiveBridge({ packageId: packageId || null }))
        }

        if (!isBridgeHydrated(bridge.value)) {
          throw new Error('Bridge hydration failed')
        }
        return bridge.value
      } catch (err) {
        error.value = studentSafeMessage(err, 'Unable to load your scene')
        throw err
      } finally {
        loading.value = false
        hydrateInFlight = null
      }
    })()

    return hydrateInFlight
  }

  async function prepare({ packageId } = {}) {
    busy.value = true
    clearError()
    try {
      return apply(await prepareSpeakingLiveBridge({ packageId }))
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to build your scene')
      throw err
    } finally {
      busy.value = false
    }
  }

  async function startPractice({ packageId } = {}) {
    busy.value = true
    clearError()
    try {
      return apply(await startSpeakingRehearsal({ packageId }))
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to enter the scene')
      throw err
    } finally {
      busy.value = false
    }
  }

  async function submitTurn() {
    const text = (draft.value || '').trim()
    if (!text) return
    busy.value = true
    clearError()
    try {
      const result = apply(await submitSpeakingRehearsalTurn(text))
      draft.value = ''
      return result
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to continue the scene')
      throw err
    } finally {
      busy.value = false
    }
  }

  async function finishRehearsal() {
    busy.value = true
    clearError()
    try {
      return apply(await completeSpeakingRehearsal())
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to get ready for the live scene')
      throw err
    } finally {
      busy.value = false
    }
  }

  /**
   * M12 voice turn — POST /rehearsal/respond, then mirror LiveBridgeOut.
   * Returns the full respond payload (transcript, decision, audio, bridge).
   */
  async function respondVoice(audioBlob, { filename } = {}) {
    busy.value = true
    clearError()
    try {
      const data = await respondSpeakingRehearsal(audioBlob, { filename })
      if (data?.bridge) apply(data.bridge)
      return data
    } catch (err) {
      error.value = studentSafeMessage(err, 'Unable to continue the scene')
      throw err
    } finally {
      busy.value = false
    }
  }

  return {
    loading,
    busy,
    error,
    bridge,
    draft,
    journeyPhase,
    preparation,
    rehearsal,
    voiceSession,
    liveContext,
    readyForLive,
    turns,
    hydrated,
    loadBridge,
    ensureHydrated,
    prepare,
    startPractice,
    submitTurn,
    finishRehearsal,
    respondVoice,
    apply,
    clearError,
  }
}
