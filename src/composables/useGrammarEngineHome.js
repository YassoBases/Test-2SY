/**
 * Grammar UI V2 — read-only engine projection for the Grammar page.
 * Consumes Journey graph + Grammar dashboard/lesson + Adaptive insights.
 * Never invents unlocks; never writes Journey/Progression/Mastery.
 */
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchLearningJourney } from '../api/learningJourney.js'
import { fetchAdaptiveInsights } from '../api/adaptiveInsights.js'
import {
  completeGrammarActivity,
  fetchGrammarDashboard,
  startGrammarLesson,
} from '../api/grammar.js'
import { getErrorMessage } from '../api/client.js'
import { ROUTES } from '../constants/app.js'
import { useGrammarModule } from './useGrammarModule.js'
import {
  hasCanonicalGrammarLessonContent,
  useGrammarLessonSession,
} from './useGrammarLessonSession.js'

const COMPLETION_STORAGE_KEY = 'eduspark.grammar.completion.v1'
const STALE_GRAMMAR_SESSION_CODES = new Set([
  'invalid_session_id',
  'session_not_found',
  'session_expired',
  'session_not_open',
])
const STALE_GRAMMAR_SESSION_MESSAGE =
  'This Grammar lesson session expired. Start a fresh lesson to continue.'

const journey = ref(null)
const dashboard = ref(null)
const adaptive = ref(null)
const completionResult = ref(null)
const loading = ref(false)
const starting = ref(false)
const completing = ref(false)
/** Machine key for empty-state branches: 'load' | 'lesson' | 'complete' | '' */
const errorMessage = ref('')
/** Human-readable API / action error — always surface to the user. */
const actionError = ref('')

function hydrateCompletion() {
  if (completionResult.value) return
  try {
    const raw = sessionStorage.getItem(COMPLETION_STORAGE_KEY)
    if (raw) completionResult.value = JSON.parse(raw)
  } catch {
    /* ignore */
  }
}

function persistCompletion(payload) {
  completionResult.value = payload
  try {
    if (payload) sessionStorage.setItem(COMPLETION_STORAGE_KEY, JSON.stringify(payload))
    else sessionStorage.removeItem(COMPLETION_STORAGE_KEY)
  } catch {
    /* ignore */
  }
}

function isStaleGrammarSessionError(err) {
  const detail = err?.response?.data?.detail
  const code = err?.response?.data?.code || detail?.code || err?.code || ''
  const message = [
    typeof detail === 'string' ? detail : '',
    typeof detail?.message === 'string' ? detail.message : '',
    err?.message || '',
  ].join(' ')

  return (
    STALE_GRAMMAR_SESSION_CODES.has(code) ||
    /activity session (not found|has expired|status is|is not a valid uuid)/i.test(message)
  )
}

export function useGrammarEngineHome() {
  const router = useRouter()
  const { isEnabled, isReady, loading: statusLoading, refresh } = useGrammarModule()
  const { activeLesson, hasActiveLesson, saveLesson, clearLesson, hydrate } = useGrammarLessonSession()

  const levels = computed(() => journey.value?.levels || [])
  const progress = computed(() => journey.value?.progress || null)
  const anchorCefr = computed(
    () =>
      journey.value?.anchor_cefr ||
      journey.value?.progress?.cefr_label ||
      '',
  )
  const currentGrammarId = computed(() => journey.value?.current_grammar_id || null)
  const nextGrammarId = computed(() => journey.value?.next_grammar_id || null)
  const journeyEnabled = computed(() => !!journey.value?.enabled)

  const currentStage = computed(() => {
    const id = currentGrammarId.value
    if (!id) return null
    for (const lv of levels.value) {
      const found = (lv.stages || []).find((s) => s.grammar_id === id)
      if (found) return { ...found, cefr: lv.cefr }
    }
    return null
  })

  const nextStage = computed(() => {
    const id = nextGrammarId.value
    if (!id) return null
    for (const lv of levels.value) {
      const found = (lv.stages || []).find((s) => s.grammar_id === id)
      if (found) return { ...found, cefr: lv.cefr }
    }
    return null
  })

  const stageCount = computed(() =>
    levels.value.reduce((acc, lv) => acc + (lv.stages?.length || 0), 0),
  )

  const completedStages = computed(() => {
    const out = []
    for (const lv of levels.value) {
      for (const s of lv.stages || []) {
        if (s.status === 'completed') out.push({ ...s, cefr: lv.cefr })
      }
    }
    return out
  })

  const completedByLevel = computed(() => {
    const map = {}
    for (const s of completedStages.value) {
      if (!map[s.cefr]) map[s.cefr] = []
      map[s.cefr].push(s)
    }
    return map
  })

  const remainingTopics = computed(() => {
    const total = progress.value?.overall_total || 0
    const done = progress.value?.overall_completed || 0
    return Math.max(0, total - done)
  })

  const overallPercent = computed(() => {
    const total = progress.value?.overall_total || 0
    const done = progress.value?.overall_completed || 0
    if (!total) return 0
    return Math.round((100 * done) / total)
  })

  const estimatedMinutes = computed(
    () =>
      currentStage.value?.estimated_minutes ||
      dashboard.value?.estimated_minutes ||
      18,
  )

  const lessonGoal = computed(
    () => dashboard.value?.lesson_goal || currentStage.value?.display_name || '',
  )

  const averageConfidence = computed(() => adaptive.value?.profile?.average_confidence ?? 0)

  const recommendation = computed(() => {
    if (dashboard.value?.lesson_goal) return dashboard.value.lesson_goal
    const focus = adaptive.value?.teacher?.focus_display_name
    if (focus) return focus
    return currentStage.value?.display_name || ''
  })

  function stageById(grammarId) {
    if (!grammarId) return null
    for (const lv of levels.value) {
      const found = (lv.stages || []).find((s) => s.grammar_id === grammarId)
      if (found) return { ...found, cefr: lv.cefr }
    }
    return null
  }

  function canOpenStage(stage) {
    if (!stage) return false
    return stage.status === 'current' || stage.status === 'completed'
  }

  function canStartLessonFor(stage) {
    if (!isEnabled.value || starting.value) return false
    // Hero CTA: allow when the journey names a current topic.
    if (!stage) return !!currentGrammarId.value
    if (stage.status === 'current') return true
    // Same topic as journey current (status mismatch must not disable the CTA).
    return !!currentGrammarId.value && stage.grammar_id === currentGrammarId.value
  }

  async function loadHome() {
    loading.value = true
    errorMessage.value = ''
    actionError.value = ''
    hydrate()
    hydrateCompletion()
    try {
      await refresh()
      if (!isEnabled.value) {
        journey.value = null
        dashboard.value = null
        return
      }
      const [j, d, a] = await Promise.all([
        fetchLearningJourney(),
        fetchGrammarDashboard().catch(() => null),
        fetchAdaptiveInsights().catch(() => null),
      ])
      journey.value = j
      dashboard.value = d
      adaptive.value = a
    } catch (err) {
      errorMessage.value = 'load'
      actionError.value = getErrorMessage(err)
      journey.value = null
    } finally {
      loading.value = false
    }
  }

  async function startCurrentLesson({ grammarId = null, navigate = true } = {}) {
    const stage = grammarId ? stageById(grammarId) : currentStage.value
    const targetId = stage?.grammar_id || grammarId || currentGrammarId.value

    if (starting.value) return null

    if (!isEnabled.value) {
      errorMessage.value = 'lesson'
      actionError.value = 'Grammar module is not available.'
      return null
    }

    // Locked / unlocked (non-current) stages must not start; completed may reopen.
    if (stage && stage.status !== 'current' && stage.status !== 'completed') {
      errorMessage.value = 'lesson'
      actionError.value = `This topic is ${stage.status} and cannot be started.`
      return null
    }

    if (!stage && !currentGrammarId.value) {
      errorMessage.value = 'lesson'
      actionError.value = 'No current grammar topic is available yet.'
      return null
    }

    starting.value = true
    errorMessage.value = ''
    actionError.value = ''
    try {
      const lesson = await startGrammarLesson({ use_llm_authoring: true })
      if (!lesson?.lesson_id) {
        errorMessage.value = 'lesson'
        actionError.value = 'Lesson start succeeded but returned an empty package.'
        return null
      }
      if (lesson.authoring_status === 'retry_required') {
        clearLesson()
        errorMessage.value = 'lesson'
        actionError.value =
          lesson.retry_message || 'The lesson could not be prepared correctly. Please try creating it again.'
        return null
      }
      if (!hasCanonicalGrammarLessonContent(lesson)) {
        clearLesson()
        errorMessage.value = 'lesson'
        actionError.value = 'The lesson package is not ready yet. Start a fresh Grammar lesson.'
        return null
      }
      saveLesson(lesson)
      if (navigate) {
        const id = targetId || 'current'
        await router.push(ROUTES.STUDENT_GRAMMAR_TOPIC(id))
      }
      return lesson
    } catch (err) {
      errorMessage.value = 'lesson'
      actionError.value = getErrorMessage(err)
      return null
    } finally {
      starting.value = false
    }
  }

  async function openStage(stage) {
    if (!canOpenStage(stage)) return false
    if (stage.status === 'current') {
      await startCurrentLesson({ grammarId: stage.grammar_id })
      return true
    }
    if (stage.status === 'completed') {
      await startCurrentLesson({ grammarId: stage.grammar_id })
      return true
    }
    return false
  }

  async function finishLesson() {
    const lesson = activeLesson.value
    if (!lesson?.activity_session_id) {
      clearLesson()
      errorMessage.value = 'lesson'
      actionError.value = STALE_GRAMMAR_SESSION_MESSAGE
      await router.push(ROUTES.STUDENT_GRAMMAR)
      return null
    }
    completing.value = true
    errorMessage.value = ''
    actionError.value = ''
    try {
      const result = await completeGrammarActivity({
        activity_session_id: lesson.activity_session_id,
        language_id: 1,
        response_text: '',
      })
      const stage = stageById(result.grammar_id) || currentStage.value
      persistCompletion({
        ...result,
        display_name: stage?.display_name || lesson.grammar_target || '',
        skills: stage?.skills || [],
        confidence: averageConfidence.value,
        next_display_name: nextStage.value?.display_name || '',
      })
      clearLesson()
      await loadHome()
      await router.push(ROUTES.STUDENT_GRAMMAR_COMPLETE)
      return result
    } catch (err) {
      if (isStaleGrammarSessionError(err)) {
        clearLesson()
        await loadHome().catch(() => null)
        errorMessage.value = 'lesson'
        actionError.value = STALE_GRAMMAR_SESSION_MESSAGE
        await router.push(ROUTES.STUDENT_GRAMMAR)
        return null
      }
      errorMessage.value = 'complete'
      actionError.value = getErrorMessage(err)
      return null
    } finally {
      completing.value = false
    }
  }

  function clearCompletion() {
    persistCompletion(null)
  }

  return {
    journey,
    dashboard,
    adaptive,
    completionResult,
    loading,
    starting,
    completing,
    errorMessage,
    actionError,
    isEnabled,
    isReady,
    statusLoading,
    activeLesson,
    hasActiveLesson,
    levels,
    progress,
    anchorCefr,
    currentGrammarId,
    nextGrammarId,
    journeyEnabled,
    currentStage,
    nextStage,
    stageCount,
    completedStages,
    completedByLevel,
    remainingTopics,
    overallPercent,
    estimatedMinutes,
    lessonGoal,
    averageConfidence,
    recommendation,
    stageById,
    canOpenStage,
    canStartLessonFor,
    loadHome,
    startCurrentLesson,
    openStage,
    finishLesson,
    clearLesson,
    clearCompletion,
    hydrate,
    hydrateCompletion,
  }
}
