import { computed, onUnmounted, ref } from 'vue'
import {
  applyListeningOfficialPromotion,
  fetchListeningPromotionStatus,
  startListeningPromotionTest,
  submitListeningPromotionTest,
} from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

/** Shared listening promotion state — one status fetch per screen lifecycle. */
const status = ref(null)
const statusLoading = ref(false)
const statusError = ref('')
const session = ref(null)
const sessionLoading = ref(false)
const sessionError = ref('')
const submitResult = ref(null)
const submitLoading = ref(false)
const submitError = ref('')
const promotionResult = ref(null)
const promoteLoading = ref(false)
const promoteError = ref('')
const phase = ref('dashboard')

let statusPromise = null
let listeners = 0

export function useListeningPromotion() {
  const canStartTest = computed(() => {
    const readinessStatus = status.value?.readiness?.status
    return Boolean(status.value?.eligibility?.eligible && readinessStatus === 'PROMOTION_AVAILABLE')
  })

  const hasActiveSession = computed(() => Boolean(status.value?.active_session?.session_id))

  const assessments = computed(() => session.value?.assessments || [])

  const mcqQuestions = computed(() =>
    assessments.value.map((item) => ({
      id: item.assessment_id,
      stem: item.question,
      choices: item.choices || [],
      situation: item.situation,
      objectiveLabel: item.objective_label,
      sequenceIndex: item.sequence_index,
    })),
  )

  const expiresAtMs = computed(() => {
    const raw = session.value?.expires_at || status.value?.active_session?.expires_at
    if (!raw) return null
    const ms = new Date(raw).getTime()
    return Number.isFinite(ms) ? ms : null
  })

  async function loadStatus({ force = false } = {}) {
    if (!force && status.value && !statusError.value) return status.value
    if (statusPromise) return statusPromise

    statusLoading.value = true
    statusError.value = ''
    statusPromise = fetchListeningPromotionStatus()
      .then((data) => {
        status.value = data
        return data
      })
      .catch((err) => {
        statusError.value = getErrorMessage(err, 'Could not load promotion status')
        throw err
      })
      .finally(() => {
        statusLoading.value = false
        statusPromise = null
      })

    return statusPromise
  }

  async function beginTest({ resume = false } = {}) {
    sessionLoading.value = true
    sessionError.value = ''
    submitResult.value = null
    promotionResult.value = null
    promoteError.value = ''
    try {
      const data = await startListeningPromotionTest()
      session.value = data
      phase.value = 'session'
      if (status.value?.active_session) {
        status.value = {
          ...status.value,
          active_session: {
            ...status.value.active_session,
            session_id: data.session_id,
            expires_at: data.expires_at,
            assessment_count: data.assessments?.length || status.value.active_session.assessment_count,
          },
        }
      }
      return data
    } catch (err) {
      sessionError.value = formatPromotionApiError(err, 'Could not start promotion test')
      throw err
    } finally {
      sessionLoading.value = false
    }
  }

  async function resumeActiveSession() {
    return beginTest({ resume: true })
  }

  async function submitTest(answers) {
    if (!session.value?.session_id) {
      submitError.value = 'No active promotion session'
      return null
    }
    submitLoading.value = true
    submitError.value = ''
    try {
      const payload = {}
      for (const [assessmentId, choiceIndex] of Object.entries(answers || {})) {
        if (choiceIndex === undefined || choiceIndex === null || choiceIndex === '') continue
        payload[assessmentId] = Number(choiceIndex)
      }
      const data = await submitListeningPromotionTest({
        sessionId: session.value.session_id,
        answers: payload,
      })
      submitResult.value = data
      phase.value = 'result'
      session.value = null
      await loadStatus({ force: true })
      return data
    } catch (err) {
      submitError.value = formatPromotionApiError(err, 'Could not submit promotion test')
      if (err?.response?.status === 409 || err?.response?.status === 410) {
        await loadStatus({ force: true })
      }
      throw err
    } finally {
      submitLoading.value = false
    }
  }

  async function promote() {
    promoteLoading.value = true
    promoteError.value = ''
    try {
      const data = await applyListeningOfficialPromotion()
      promotionResult.value = data
      phase.value = 'success'
      await loadStatus({ force: true })
      return data
    } catch (err) {
      promoteError.value = formatPromotionApiError(err, 'Could not apply official promotion')
      throw err
    } finally {
      promoteLoading.value = false
    }
  }

  function resetToDashboard() {
    phase.value = 'dashboard'
    session.value = null
    submitResult.value = null
    promotionResult.value = null
    sessionError.value = ''
    submitError.value = ''
    promoteError.value = ''
  }

  function formatPromotionApiError(err, fallback) {
    const detail = err?.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail === 'object') {
      if (detail.reason) return String(detail.reason)
      if (detail.promotion_success === false && detail.reason) return String(detail.reason)
    }
    return getErrorMessage(err, fallback)
  }

  listeners += 1
  onUnmounted(() => {
    listeners -= 1
    if (listeners <= 0) {
      status.value = null
      statusPromise = null
      resetToDashboard()
    }
  })

  return {
    status,
    statusLoading,
    statusError,
    session,
    sessionLoading,
    sessionError,
    submitResult,
    submitLoading,
    submitError,
    promotionResult,
    promoteLoading,
    promoteError,
    phase,
    canStartTest,
    hasActiveSession,
    assessments,
    mcqQuestions,
    expiresAtMs,
    loadStatus,
    beginTest,
    resumeActiveSession,
    submitTest,
    promote,
    resetToDashboard,
    formatPromotionApiError,
  }
}
