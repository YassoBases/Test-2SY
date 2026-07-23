import { computed, ref } from 'vue'
import {
  abandonSpeakingPromotionAssessment,
  completeSpeakingPromotionAssessment,
  createSpeakingPromotionAssessment,
  fetchSpeakingPromotionAssessment,
  fetchSpeakingPromotionAssessmentResult,
  fetchSpeakingPromotionStatus,
  promoteSpeakingOfficialCefr,
  retrySpeakingPromotionAssessment,
  startSpeakingPromotionAssessment,
  submitSpeakingPromotionAssessmentTask,
} from '../api/speakingPromotion.js'
import { getErrorMessage } from '../api/client.js'

/**
 * Speaking Promotion Assessment — Vue projection of S19/S20 APIs only.
 * Never computes PASS/FAIL/CEFR/bridge/retry eligibility locally.
 * S20 official CEFR writes happen only via promoteSpeakingOfficialCefr.
 */
export function useSpeakingPromotion() {
  const phase = ref('home') // home | intro | runtime | completing | result
  const status = ref(null)
  const statusLoading = ref(false)
  const statusError = ref('')
  const assessment = ref(null)
  const assessmentLoading = ref(false)
  const assessmentError = ref('')
  const startPayload = ref(null)
  const sessionLoading = ref(false)
  const sessionError = ref('')
  const submitLoading = ref(false)
  const submitError = ref('')
  const lastSubmit = ref(null)
  const result = ref(null)
  const resultLoading = ref(false)
  const resultError = ref('')
  const actionLoading = ref(false)
  const promotionResult = ref(null)
  const promoteLoading = ref(false)
  const promoteError = ref('')

  // Alias for panels that still mention blueprint
  const blueprint = assessment
  const blueprintLoading = assessmentLoading
  const blueprintError = assessmentError

  const available = computed(() => Boolean(status.value?.available))
  const spaUnlocked = computed(() => Boolean(status.value?.spa_unlocked))
  const message = computed(() => status.value?.message || '')
  const targetCefr = computed(
    () => assessment.value?.target_cefr || status.value?.target_cefr || null,
  )
  const sourceCefr = computed(
    () => assessment.value?.source_cefr || status.value?.source_cefr || null,
  )
  const estimatedDurationSeconds = computed(
    () => status.value?.estimated_duration_seconds || 0,
  )
  const tasks = computed(() => assessment.value?.tasks || [])
  const taskCount = computed(
    () =>
      assessment.value?.task_count ||
      status.value?.task_count ||
      tasks.value.length ||
      0,
  )
  const hasInteractionGaps = computed(
    () =>
      Boolean(
        assessment.value?.has_interaction_coverage_gaps ||
          status.value?.has_interaction_coverage_gaps,
      ),
  )
  const assessmentId = computed(
    () => assessment.value?.assessment_id || status.value?.assessment_id || null,
  )
  const attemptId = computed(
    () =>
      startPayload.value?.attempt_id ||
      assessment.value?.attempt_id ||
      status.value?.attempt_id ||
      null,
  )
  const backendStatus = computed(
    () => assessment.value?.status || status.value?.status || 'unavailable',
  )
  const currentTaskIndex = computed(() => {
    if (startPayload.value?.current_task_index != null) {
      return startPayload.value.current_task_index
    }
    if (assessment.value?.current_task_index != null) {
      return assessment.value.current_task_index
    }
    return 0
  })
  const currentTask = computed(() => {
    const fromStart = startPayload.value?.current_task
    if (fromStart) return fromStart
    const idx = currentTaskIndex.value
    const list = tasks.value
    if (!list.length) return null
    return list.find((t) => t.task_order === idx + 1) || list[idx] || null
  })
  const completedTaskCount = computed(() => Math.max(0, Number(currentTaskIndex.value) || 0))
  const remainingTaskCount = computed(() =>
    Math.max(0, Number(taskCount.value) - Number(completedTaskCount.value)),
  )
  const allTasksComplete = computed(() => Boolean(lastSubmit.value?.all_tasks_complete))
  const outcome = computed(() => result.value?.outcome || null)
  const homeState = computed(() => {
    if (statusLoading.value && !status.value) return 'loading'
    if (statusError.value) return 'error'
    if (!spaUnlocked.value && !assessmentId.value) return 'locked'
    const st = String(backendStatus.value || '').toLowerCase()
    if (st === 'in_progress') return 'in_progress'
    if (result.value?.outcome) {
      const o = String(result.value.outcome).toUpperCase()
      if (o === 'PASS') return 'passed'
      if (o === 'FAIL') return 'failed'
      if (o === 'ABANDONED') return 'abandoned'
      if (o === 'TIMEOUT') return 'timeout'
      if (o === 'INCOMPLETE') return 'incomplete'
      return 'completed'
    }
    if (st === 'completed' || st === 'abandoned' || st === 'unavailable') {
      return st === 'abandoned' ? 'abandoned' : 'completed'
    }
    if (assessmentId.value || available.value) return 'available'
    if (spaUnlocked.value) return 'eligible'
    return 'locked'
  })
  const canRetryProjection = computed(() => {
    const o = String(outcome.value || '').toUpperCase()
    return ['FAIL', 'ABANDONED', 'TIMEOUT', 'INCOMPLETE'].includes(o)
  })
  const canPromoteOfficial = computed(() => {
    if (promotionResult.value?.promotion_success) return false
    const o = String(outcome.value || '').toUpperCase()
    return o === 'PASS' && Boolean(result.value?.ready_for_official_promotion)
  })
  const officialPromoted = computed(() => Boolean(promotionResult.value?.promotion_success))

  function apiDetailMessage(err, fallback) {
    const detail = err?.response?.data?.detail
    if (typeof detail === 'object' && detail?.message) return detail.message
    if (typeof detail === 'string') return detail
    return getErrorMessage(err, fallback)
  }

  async function loadStatus({ force = false } = {}) {
    if (!force && status.value && !statusError.value) return status.value
    statusLoading.value = true
    statusError.value = ''
    try {
      status.value = await fetchSpeakingPromotionStatus()
      if (status.value?.assessment_id) {
        await refreshAssessment(status.value.assessment_id, { soft: true })
        const st = String(status.value?.status || assessment.value?.status || '').toLowerCase()
        if (['completed', 'abandoned', 'unavailable'].includes(st) || assessment.value?.ready_for_official_promotion) {
          await loadResult(status.value.assessment_id, { soft: true })
        }
      }
      return status.value
    } catch (err) {
      statusError.value = apiDetailMessage(err, 'Unable to load speaking assessment status')
      throw err
    } finally {
      statusLoading.value = false
    }
  }

  async function refreshAssessment(id, { soft = false } = {}) {
    const assessmentKey = id || assessmentId.value
    if (!assessmentKey) return null
    assessmentLoading.value = true
    if (!soft) assessmentError.value = ''
    try {
      assessment.value = await fetchSpeakingPromotionAssessment(assessmentKey)
      return assessment.value
    } catch (err) {
      if (!soft) {
        assessmentError.value = apiDetailMessage(err, 'Unable to load assessment')
        throw err
      }
      return null
    } finally {
      assessmentLoading.value = false
    }
  }

  /** Ensure a frozen assessment exists (create if needed). */
  async function ensureAssessment() {
    assessmentLoading.value = true
    assessmentError.value = ''
    try {
      if (status.value?.assessment_id) {
        assessment.value = await fetchSpeakingPromotionAssessment(status.value.assessment_id)
      } else if (assessment.value?.assessment_id) {
        assessment.value = await fetchSpeakingPromotionAssessment(assessment.value.assessment_id)
      } else {
        assessment.value = await createSpeakingPromotionAssessment()
      }
      await loadStatus({ force: true })
      return assessment.value
    } catch (err) {
      assessmentError.value = apiDetailMessage(
        err,
        'Speaking assessment is temporarily unavailable',
      )
      throw err
    } finally {
      assessmentLoading.value = false
    }
  }

  /** @deprecated preview-only alias — prefer openIntro / startAssessment */
  async function previewAssessment() {
    return ensureAssessment()
  }

  async function openIntro() {
    await ensureAssessment()
    phase.value = 'intro'
    return assessment.value
  }

  async function startAssessment({ resume = false } = {}) {
    sessionLoading.value = true
    sessionError.value = ''
    submitError.value = ''
    if (!resume) lastSubmit.value = null
    try {
      await ensureAssessment()
      const id = assessmentId.value
      if (!id) throw new Error('Assessment not available')
      startPayload.value = await startSpeakingPromotionAssessment(id)
      await refreshAssessment(id, { soft: true })
      phase.value = 'runtime'
      return startPayload.value
    } catch (err) {
      sessionError.value = apiDetailMessage(
        err,
        resume
          ? 'Unable to resume assessment'
          : 'Unable to start assessment',
      )
      throw err
    } finally {
      sessionLoading.value = false
    }
  }

  async function resumeAssessment() {
    return startAssessment({ resume: true })
  }

  /** From intro: start attempt if needed, then enter runtime. */
  async function beginTasks() {
    if (startPayload.value?.attempt_id && startPayload.value?.session_id) {
      phase.value = 'runtime'
      return startPayload.value
    }
    return startAssessment({ resume: false })
  }

  async function submitCurrentTask({ transcriptText = '', mediaObjectId = null } = {}) {
    const id = assessmentId.value
    const task = currentTask.value
    if (!id || !task?.task_id) {
      submitError.value = 'No current assessment task'
      return null
    }
    submitLoading.value = true
    submitError.value = ''
    try {
      lastSubmit.value = await submitSpeakingPromotionAssessmentTask(id, {
        task_id: task.task_id,
        transcript_text: transcriptText || '',
        media_object_id: mediaObjectId || null,
        attempt_id: attemptId.value || null,
      })
      // Refresh start cursor from submit projection
      if (startPayload.value) {
        startPayload.value = {
          ...startPayload.value,
          current_task_index: lastSubmit.value.current_task_index,
          current_task: null,
        }
      }
      await refreshAssessment(id, { soft: true })

      if (lastSubmit.value.all_tasks_complete) {
        await finalizeAssessment()
      } else if (lastSubmit.value.next_task_id) {
        const next = tasks.value.find((t) => t.task_id === lastSubmit.value.next_task_id)
        if (startPayload.value) {
          startPayload.value = {
            ...startPayload.value,
            current_task: next || null,
            current_task_index: lastSubmit.value.current_task_index,
          }
        }
      }
      return lastSubmit.value
    } catch (err) {
      submitError.value = apiDetailMessage(err, 'Unable to submit assessment task')
      throw err
    } finally {
      submitLoading.value = false
    }
  }

  async function finalizeAssessment() {
    const id = assessmentId.value
    if (!id) return null
    phase.value = 'completing'
    resultLoading.value = true
    resultError.value = ''
    try {
      result.value = await completeSpeakingPromotionAssessment(id)
      await loadStatus({ force: true })
      phase.value = 'result'
      return result.value
    } catch (err) {
      // If complete fails, try fetching result (idempotent terminal)
      try {
        result.value = await fetchSpeakingPromotionAssessmentResult(id)
        phase.value = 'result'
        return result.value
      } catch {
        resultError.value = apiDetailMessage(err, 'Unable to complete assessment')
        phase.value = 'runtime'
        throw err
      }
    } finally {
      resultLoading.value = false
    }
  }

  async function loadResult(id, { soft = false } = {}) {
    const key = id || assessmentId.value
    if (!key) return null
    resultLoading.value = true
    if (!soft) resultError.value = ''
    try {
      result.value = await fetchSpeakingPromotionAssessmentResult(key)
      return result.value
    } catch (err) {
      if (!soft) {
        resultError.value = apiDetailMessage(err, 'Result not available yet')
        throw err
      }
      return null
    } finally {
      resultLoading.value = false
    }
  }

  async function viewResult() {
    await loadResult()
    phase.value = 'result'
    return result.value
  }

  async function abandonAssessment() {
    const id = assessmentId.value
    if (!id) return null
    actionLoading.value = true
    sessionError.value = ''
    try {
      result.value = await abandonSpeakingPromotionAssessment(id)
      startPayload.value = null
      await loadStatus({ force: true })
      phase.value = 'result'
      return result.value
    } catch (err) {
      sessionError.value = apiDetailMessage(err, 'Unable to abandon assessment')
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function retryAssessment() {
    const id = assessmentId.value
    if (!id) return null
    sessionLoading.value = true
    sessionError.value = ''
    result.value = null
    lastSubmit.value = null
    promotionResult.value = null
    try {
      startPayload.value = await retrySpeakingPromotionAssessment(id)
      await refreshAssessment(id, { soft: true })
      phase.value = 'intro'
      return startPayload.value
    } catch (err) {
      sessionError.value = apiDetailMessage(err, 'Retry is not available right now')
      throw err
    } finally {
      sessionLoading.value = false
    }
  }

  async function promoteOfficial() {
    promoteLoading.value = true
    promoteError.value = ''
    try {
      const data = await promoteSpeakingOfficialCefr({
        assessmentId: assessmentId.value,
        attemptId: result.value?.attempt_id || attemptId.value,
      })
      promotionResult.value = data
      if (result.value) {
        result.value = {
          ...result.value,
          ready_for_official_promotion: false,
        }
      }
      await loadStatus({ force: true })
      return data
    } catch (err) {
      const detail = err?.response?.data?.detail
      // Idempotent already-promoted: 409 with success payload
      if (
        err?.response?.status === 409 &&
        typeof detail === 'object' &&
        detail?.promotion_success
      ) {
        promotionResult.value = detail
        if (result.value) {
          result.value = { ...result.value, ready_for_official_promotion: false }
        }
        return detail
      }
      promoteError.value = apiDetailMessage(err, 'Unable to apply official speaking level')
      throw err
    } finally {
      promoteLoading.value = false
    }
  }

  function backToHome() {
    phase.value = 'home'
    startPayload.value = null
    sessionError.value = ''
    submitError.value = ''
  }

  function goHomeAndRefresh() {
    backToHome()
    return loadStatus({ force: true })
  }

  return {
    phase,
    status,
    statusLoading,
    statusError,
    assessment,
    assessmentLoading,
    assessmentError,
    blueprint,
    blueprintLoading,
    blueprintError,
    startPayload,
    sessionLoading,
    sessionError,
    submitLoading,
    submitError,
    lastSubmit,
    result,
    resultLoading,
    resultError,
    actionLoading,
    available,
    spaUnlocked,
    message,
    targetCefr,
    sourceCefr,
    estimatedDurationSeconds,
    tasks,
    taskCount,
    hasInteractionGaps,
    assessmentId,
    attemptId,
    backendStatus,
    currentTaskIndex,
    currentTask,
    completedTaskCount,
    remainingTaskCount,
    allTasksComplete,
    outcome,
    homeState,
    canRetryProjection,
    canPromoteOfficial,
    officialPromoted,
    promotionResult,
    promoteLoading,
    promoteError,
    loadStatus,
    ensureAssessment,
    previewAssessment,
    openIntro,
    startAssessment,
    resumeAssessment,
    beginTasks,
    submitCurrentTask,
    finalizeAssessment,
    loadResult,
    viewResult,
    abandonAssessment,
    retryAssessment,
    promoteOfficial,
    backToHome,
    goHomeAndRefresh,
    refreshAssessment,
  }
}
