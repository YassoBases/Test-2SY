import { computed, ref } from 'vue'
import {
  completeSpeakingJourneyActivity,
  fetchSpeakingJourney,
  finalizeSpeakingJourneySession,
  prepareSpeakingJourneyForLive,
  startSpeakingJourneySession,
} from '../api/speakingJourney.js'
import { getErrorMessage } from '../api/client.js'
import { studentSafeJourneyError, classifySpeakingError } from '../utils/speakingRuntimeMeta.js'

/**
 * Projection-only Speaking journey state — no educational decision logic.
 * Prefers S12 `read_model` when present.
 */
export function useSpeakingJourney() {
  const journey = ref(null)
  const loading = ref(false)
  const error = ref('')
  const starting = ref(false)
  const advancing = ref(false)
  const preparingLive = ref(false)
  const sessionOutcome = ref(null)
  const lastStarted = ref(null)
  const liveTaskPrompt = ref('')
  const journeyLiveSessionId = ref('')

  const readModel = computed(() => journey.value?.read_model || null)

  const focusLabel = computed(
    () => readModel.value?.focus_label || journey.value?.current_focus_label || '',
  )
  const focusReason = computed(
    () => readModel.value?.focus_reason || journey.value?.current_focus_reason || '',
  )
  const officialCefr = computed(
    () => readModel.value?.official_cefr || journey.value?.official_level || '',
  )
  const internalStage = computed(() => readModel.value?.internal_stage || null)
  const alexRemainingSeconds = computed(() => {
    const n = readModel.value?.alex_daily_remaining_seconds
    return typeof n === 'number' ? n : null
  })
  const promotionReadiness = computed(() => readModel.value?.promotion_readiness || null)
  const spaUnlocked = computed(() => Boolean(promotionReadiness.value?.spa_unlocked))
  const currentMission = computed(() => readModel.value?.current_mission || null)
  const currentTask = computed(() => readModel.value?.current_task || null)
  const attempt = computed(() => readModel.value?.attempt || null)
  const learningPath = computed(() => readModel.value?.learning_path || [])
  const support = computed(() => readModel.value?.support || [])
  const teachingBlocks = computed(() => readModel.value?.teaching_blocks || [])
  const weakSkills = computed(() => readModel.value?.weak_skills || [])
  const improvingSkills = computed(() => readModel.value?.improving_skills || [])
  const retentionNeeded = computed(() => readModel.value?.retention_needed || [])
  const transferNeeded = computed(() => readModel.value?.transfer_needed || [])
  const nextMission = computed(() => readModel.value?.next_mission || null)
  const hasActiveSession = computed(
    () => Boolean(readModel.value?.has_active_session || journey.value?.has_active_session),
  )
  const practiceWithAlexAvailable = computed(
    () => journey.value?.practice_with_alex_available !== false,
  )
  const todaySteps = computed(() => journey.value?.steps || [])
  const todayMissions = computed(() => journey.value?.today_missions || [])
  const expectedOutcome = computed(() => readModel.value?.expected_outcome || '')
  const objectives = computed(() => readModel.value?.objectives || [])
  const planSummary = computed(() => journey.value?.plan_summary || '')
  const lessonTitle = computed(
    () => journey.value?.lesson_title || journey.value?.session_goal || focusLabel.value || '',
  )
  const currentActivityId = computed(() => journey.value?.current_activity_id || '')
  const currentActivityInstructions = computed(
    () => journey.value?.current_activity_instructions || '',
  )
  const currentActivityTitle = computed(
    () => journey.value?.current_activity_title || '',
  )
  const currentActivityKind = computed(() => journey.value?.current_activity_kind || '')
  const activitiesTotal = computed(() => Number(journey.value?.activities_total || 0))
  const activitiesCompleted = computed(() => Number(journey.value?.activities_completed || 0))
  const activitiesRemaining = computed(() => Number(journey.value?.activities_remaining || 0))
  const liveExecutionReady = computed(() => Boolean(journey.value?.live_execution_ready))
  const canContinueActivity = computed(
    () => Boolean(hasActiveSession.value && currentActivityId.value && !liveExecutionReady.value),
  )
  const hasPlan = computed(() => Boolean(readModel.value?.has_plan))
  const hasBlueprint = computed(() => Boolean(readModel.value?.has_blueprint))
  const improvingSkillsAvailable = computed(() =>
    Boolean(readModel.value?.improving_skills_available),
  )
  const retentionSignalPresent = computed(() =>
    Boolean(readModel.value?.retention_signal_present),
  )
  const transferSignalPresent = computed(() =>
    Boolean(readModel.value?.transfer_signal_present),
  )
  const todaySessionPhase = computed(() => journey.value?.today_session_phase || '')
  const nextRecommendation = computed(() => journey.value?.next_recommendation || '')
  const returningFromAlex = ref(false)
  const errorKind = ref('')

  function setSafeError(err, fallback) {
    const raw = getErrorMessage(err, fallback)
    errorKind.value = classifySpeakingError(raw)
    error.value = studentSafeJourneyError(raw, fallback)
  }

  function clearError() {
    error.value = ''
    errorKind.value = ''
  }

  async function loadJourney({ force = false } = {}) {
    if (!force && journey.value && !error.value) return journey.value
    loading.value = true
    error.value = ''
    errorKind.value = ''
    try {
      journey.value = await fetchSpeakingJourney()
      return journey.value
    } catch (err) {
      setSafeError(err, 'Unable to load speaking journey')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function startSession() {
    starting.value = true
    sessionOutcome.value = null
    returningFromAlex.value = false
    clearError()
    try {
      const started = await startSpeakingJourneySession()
      lastStarted.value = started
      // Do not hand off to LiveShell yet — Continue / prepare-live owns Talk-with-Alex entry.
      liveTaskPrompt.value =
        started.task_prompt || started.alex_context?.communicative_scenario || ''
      await loadJourney({ force: true })
      return started
    } catch (err) {
      setSafeError(err, 'Unable to start speaking session')
      throw err
    } finally {
      starting.value = false
    }
  }

  function isFinalizeOutcome(raw) {
    return Boolean(raw && typeof raw === 'object' && raw.outcome_kind != null && raw.outcome_kind !== '')
  }

  async function continueActivity() {
    const activityId = currentActivityId.value
    if (!activityId) return null
    advancing.value = true
    clearError()
    try {
      const raw = await completeSpeakingJourneyActivity(activityId)
      // Last activity auto-finalizes via existing finalize_speaking_session — same outcome shape.
      if (isFinalizeOutcome(raw)) {
        sessionOutcome.value = raw
      } else {
        lastStarted.value = {
          ...(lastStarted.value || {}),
          current_activity: raw.current_activity || null,
          phase: raw.phase,
        }
      }
      await loadJourney({ force: true })
      return raw
    } catch (err) {
      setSafeError(err, 'Unable to continue speaking session')
      throw err
    } finally {
      advancing.value = false
    }
  }

  async function prepareForLiveAlex() {
    preparingLive.value = true
    sessionOutcome.value = null
    returningFromAlex.value = false
    clearError()
    try {
      const prepared = await prepareSpeakingJourneyForLive()
      lastStarted.value = prepared
      journeyLiveSessionId.value = prepared.live_session_id || ''
      liveTaskPrompt.value =
        prepared.task_prompt || prepared.alex_context?.communicative_scenario || ''
      await loadJourney({ force: true })
      return prepared
    } catch (err) {
      setSafeError(err, 'Unable to prepare Talk with Alex')
      throw err
    } finally {
      preparingLive.value = false
    }
  }

  function clearLiveHandoff() {
    liveTaskPrompt.value = ''
    journeyLiveSessionId.value = ''
  }

  async function onLiveSessionEnded() {
    returningFromAlex.value = true
    try {
      if (hasActiveSession.value || journeyLiveSessionId.value) {
        sessionOutcome.value = await finalizeSpeakingJourneySession()
      }
      await loadJourney({ force: true })
    } catch (err) {
      setSafeError(err, 'Unable to finalize speaking session')
      await loadJourney({ force: true })
    } finally {
      clearLiveHandoff()
    }
  }

  function clearReturningFromAlex() {
    returningFromAlex.value = false
  }

  function clearSessionOutcome() {
    sessionOutcome.value = null
    returningFromAlex.value = false
  }

  return {
    journey,
    loading,
    error,
    errorKind,
    starting,
    advancing,
    preparingLive,
    sessionOutcome,
    lastStarted,
    liveTaskPrompt,
    journeyLiveSessionId,
    readModel,
    focusLabel,
    focusReason,
    officialCefr,
    internalStage,
    alexRemainingSeconds,
    promotionReadiness,
    spaUnlocked,
    currentMission,
    currentTask,
    attempt,
    learningPath,
    support,
    teachingBlocks,
    weakSkills,
    improvingSkills,
    retentionNeeded,
    transferNeeded,
    nextMission,
    hasActiveSession,
    practiceWithAlexAvailable,
    todaySteps,
    todayMissions,
    expectedOutcome,
    objectives,
    planSummary,
    lessonTitle,
    currentActivityId,
    currentActivityInstructions,
    currentActivityTitle,
    currentActivityKind,
    activitiesTotal,
    activitiesCompleted,
    activitiesRemaining,
    liveExecutionReady,
    canContinueActivity,
    hasPlan,
    hasBlueprint,
    improvingSkillsAvailable,
    retentionSignalPresent,
    transferSignalPresent,
    todaySessionPhase,
    nextRecommendation,
    returningFromAlex,
    loadJourney,
    startSession,
    continueActivity,
    prepareForLiveAlex,
    clearLiveHandoff,
    onLiveSessionEnded,
    clearReturningFromAlex,
    clearSessionOutcome,
    clearError,
  }
}
