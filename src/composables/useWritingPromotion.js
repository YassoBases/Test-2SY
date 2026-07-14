import { computed, onUnmounted, ref } from 'vue'
import {
  applyWritingOfficialPromotion,
  fetchWritingPromotionStatus,
  startWritingPromotionTest,
  submitWritingPromotionTest,
} from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

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

export function useWritingPromotion() {
  const canStartTest = computed(() => {
    const readinessStatus = status.value?.readiness?.status
    return Boolean(status.value?.eligibility?.eligible && readinessStatus === 'PROMOTION_AVAILABLE')
  })

  const hasActiveSession = computed(() => Boolean(status.value?.active_session?.session_id))

  const tasks = computed(() => session.value?.tasks || [])

  async function loadStatus({ force = false } = {}) {
    if (!force && status.value && !statusError.value) return status.value
    if (statusPromise) return statusPromise

    statusLoading.value = true
    statusError.value = ''
    statusPromise = fetchWritingPromotionStatus()
      .then((data) => {
        status.value = data
        return data
      })
      .catch((err) => {
        statusError.value = getErrorMessage(err, 'Could not load writing promotion status')
        throw err
      })
      .finally(() => {
        statusLoading.value = false
        statusPromise = null
      })

    return statusPromise
  }

  async function beginTest() {
    sessionLoading.value = true
    sessionError.value = ''
    submitResult.value = null
    promotionResult.value = null
    promoteError.value = ''
    try {
      const data = await startWritingPromotionTest()
      session.value = data
      phase.value = 'session'
      return data
    } catch (err) {
      sessionError.value = formatPromotionApiError(err, 'Could not start WPA')
      throw err
    } finally {
      sessionLoading.value = false
    }
  }

  async function resumeActiveSession() {
    return beginTest()
  }

  async function submitTest(submissions) {
    if (!session.value?.session_id) {
      submitError.value = 'No active WPA session'
      return null
    }
    submitLoading.value = true
    submitError.value = ''
    try {
      const data = await submitWritingPromotionTest({
        sessionId: session.value.session_id,
        submissions: submissions || {},
      })
      submitResult.value = data
      phase.value = 'result'
      session.value = null
      await loadStatus({ force: true })
      return data
    } catch (err) {
      submitError.value = formatPromotionApiError(err, 'Could not submit WPA')
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
      const data = await applyWritingOfficialPromotion()
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
    tasks,
    loadStatus,
    beginTest,
    resumeActiveSession,
    submitTest,
    promote,
    resetToDashboard,
    formatPromotionApiError,
  }
}
