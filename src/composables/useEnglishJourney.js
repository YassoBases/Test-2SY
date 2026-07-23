import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchLearningJourney } from '../api/learningJourney.js'
import { fetchTeacherStatus, startTeacherSession } from '../api/aiTeacher.js'
import { fetchAdaptiveInsights } from '../api/adaptiveInsights.js'
import { ROUTES } from '../constants/app.js'
import { useAuth } from './useAuth.js'

const SESSION_STORAGE_KEY = 'eduspark_english_journey_teacher_session'

const journey = ref(null)
const adaptive = ref(null)
const teacherEnabled = ref(true)
const teacherSession = ref(null)
const loading = ref(false)
const starting = ref(false)
const errorMessage = ref('')

function hydrateSession() {
  if (teacherSession.value) return
  try {
    const raw = sessionStorage.getItem(SESSION_STORAGE_KEY)
    if (raw) teacherSession.value = JSON.parse(raw)
  } catch {
    /* ignore corrupt cache */
  }
}

function persistSession(session) {
  teacherSession.value = session
  try {
    if (session) {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
    } else {
      sessionStorage.removeItem(SESSION_STORAGE_KEY)
    }
  } catch {
    /* quota / private mode */
  }
}

export function useEnglishJourney() {
  const router = useRouter()
  const { user } = useAuth()

  const studentName = computed(() => user.value?.name || user.value?.full_name || '')

  const enabled = computed(() => !!journey.value?.enabled)
  const progress = computed(() => journey.value?.progress || null)
  const levels = computed(() => journey.value?.levels || [])
  const currentGrammarId = computed(() => journey.value?.current_grammar_id || null)
  const nextGrammarId = computed(() => journey.value?.next_grammar_id || null)

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

  const streakDays = computed(() => adaptive.value?.profile?.learning_streak_days ?? 0)
  const averageConfidence = computed(() => adaptive.value?.profile?.average_confidence ?? 0)

  const sessionMinutes = computed(() => {
    const sections = teacherSession.value?.sections || []
    const sum = sections.reduce((acc, s) => acc + (Number(s.estimated_minutes) || 0), 0)
    if (sum > 0) return sum
    return currentStage.value?.estimated_minutes || 18
  })

  const todayGoal = computed(() => {
    const goals = teacherSession.value?.goals || []
    return goals[0]?.title || currentStage.value?.display_name || ''
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
    return stage.status === 'current' || stage.status === 'completed' || stage.status === 'unlocked'
  }

  function canStartSessionFor(stage) {
    if (!teacherEnabled.value) return false
    if (!stage) return !!currentGrammarId.value
    return stage.status === 'current' || stage.grammar_id === currentGrammarId.value
  }

  async function loadJourney({ withAdaptive = true, withTeacherStatus = true } = {}) {
    loading.value = true
    errorMessage.value = ''
    hydrateSession()
    try {
      const tasks = [fetchLearningJourney()]
      if (withAdaptive) tasks.push(fetchAdaptiveInsights().catch(() => null))
      if (withTeacherStatus) tasks.push(fetchTeacherStatus().catch(() => ({ enabled: false })))
      const [j, a, t] = await Promise.all(tasks)
      journey.value = j
      if (withAdaptive) adaptive.value = a
      if (withTeacherStatus) teacherEnabled.value = t?.enabled !== false
    } catch {
      errorMessage.value = 'load'
      journey.value = null
    } finally {
      loading.value = false
    }
  }

  async function startTodaysSession({ navigate = true } = {}) {
    if (starting.value || !teacherEnabled.value) return null
    starting.value = true
    errorMessage.value = ''
    try {
      const res = await startTeacherSession()
      if (!res?.enabled || !res?.session || !Object.keys(res.session).length) {
        teacherEnabled.value = false
        errorMessage.value = 'session'
        return null
      }
      persistSession(res.session)
      if (navigate) {
        await router.push(ROUTES.STUDENT_ENGLISH_JOURNEY_SESSION)
      }
      return res.session
    } catch {
      errorMessage.value = 'session'
      return null
    } finally {
      starting.value = false
    }
  }

  async function openStage(grammarId) {
    const stage = stageById(grammarId)
    if (!canOpenStage(stage)) return false
    await router.push(ROUTES.STUDENT_ENGLISH_JOURNEY_STAGE(grammarId))
    return true
  }

  async function finishSession() {
    await loadJourney({ withAdaptive: true, withTeacherStatus: false })
    await router.push(ROUTES.STUDENT_ENGLISH_JOURNEY_COMPLETE)
  }

  function clearSession() {
    persistSession(null)
  }

  return {
    journey,
    adaptive,
    teacherEnabled,
    teacherSession,
    loading,
    starting,
    errorMessage,
    studentName,
    enabled,
    progress,
    levels,
    currentGrammarId,
    nextGrammarId,
    currentStage,
    nextStage,
    completedStages,
    completedByLevel,
    streakDays,
    averageConfidence,
    sessionMinutes,
    todayGoal,
    stageById,
    canOpenStage,
    canStartSessionFor,
    loadJourney,
    startTodaysSession,
    openStage,
    finishSession,
    clearSession,
    hydrateSession,
  }
}
