/**
 * AI Grammar Session V3 — frontend session runtime (P0).
 * Stage machine + memory + resume. No backend persistence. No engine writes.
 */
import { computed, onScopeDispose, ref, watch } from 'vue'
import {
  GRAMMAR_SESSION_STAGES,
  SESSION_STATUS,
  SESSION_VOICE_STATES,
} from '../constants/grammarSessionStages.js'

const STORAGE_KEY = 'eduspark.grammar.sessionRuntime.v1'

function emptyMemory() {
  return {
    answers: {},
    notes: '',
    teacherContext: {},
  }
}

function readStorage(lessonId) {
  if (!lessonId) return null
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || parsed.lessonId !== lessonId) return null
    if (!GRAMMAR_SESSION_STAGES.includes(parsed.currentStage)) return null
    return parsed
  } catch {
    return null
  }
}

function writeStorage(payload) {
  try {
    if (!payload) {
      sessionStorage.removeItem(STORAGE_KEY)
      return
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  } catch {
    /* ignore quota */
  }
}

export function useGrammarSessionRuntime() {
  const lessonId = ref(null)
  const currentStage = ref(GRAMMAR_SESSION_STAGES[0])
  const visitedStages = ref([])
  const completedStages = ref([])
  const startedAt = ref(null)
  const elapsedSeconds = ref(0)
  const lessonStatus = ref(SESSION_STATUS.IDLE)
  const memory = ref(emptyMemory())
  const dirty = ref(false)

  /** Voice-ready placeholders (P0: no real voice). */
  const teacherVoiceState = ref(SESSION_VOICE_STATES.IDLE)
  const listeningState = ref(false)
  const speakingState = ref(false)
  const microphoneReady = ref(false)

  let tickTimer = null

  const stages = GRAMMAR_SESSION_STAGES
  const stageIndex = computed(() => stages.indexOf(currentStage.value))
  const totalStages = computed(() => stages.length)

  const progressPercent = computed(() => {
    if (!totalStages.value) return 0
    const done = completedStages.value.length
    if (lessonStatus.value === SESSION_STATUS.COMPLETED) return 100
    return Math.round((100 * done) / totalStages.value)
  })

  const canGoBack = computed(() => stageIndex.value > 0)
  const canGoNext = computed(() => stageIndex.value < totalStages.value - 1)
  const isLastStage = computed(() => currentStage.value === 'COMPLETE')
  const isComplete = computed(() => lessonStatus.value === SESSION_STATUS.COMPLETED)

  function persist() {
    if (!lessonId.value) return
    writeStorage({
      lessonId: lessonId.value,
      currentStage: currentStage.value,
      visitedStages: [...visitedStages.value],
      completedStages: [...completedStages.value],
      startedAt: startedAt.value,
      elapsedSeconds: elapsedSeconds.value,
      lessonStatus: lessonStatus.value,
      memory: memory.value,
    })
  }

  function markVisited(stage) {
    if (!visitedStages.value.includes(stage)) {
      visitedStages.value = [...visitedStages.value, stage]
    }
  }

  function markCompleted(stage) {
    if (!completedStages.value.includes(stage)) {
      completedStages.value = [...completedStages.value, stage]
    }
    dirty.value = true
  }

  function stopTicker() {
    if (tickTimer != null) {
      clearInterval(tickTimer)
      tickTimer = null
    }
  }

  function startTicker() {
    stopTicker()
    tickTimer = setInterval(() => {
      if (lessonStatus.value !== SESSION_STATUS.ACTIVE) return
      elapsedSeconds.value += 1
      if (elapsedSeconds.value % 15 === 0) persist()
    }, 1000)
  }

  function bindLesson(lesson) {
    const id = lesson?.lesson_id || null
    if (!id) return

    const saved = readStorage(id)
    lessonId.value = id

    if (saved) {
      currentStage.value = saved.currentStage
      visitedStages.value = Array.isArray(saved.visitedStages) ? saved.visitedStages : []
      completedStages.value = Array.isArray(saved.completedStages)
        ? saved.completedStages
        : []
      startedAt.value = saved.startedAt || new Date().toISOString()
      elapsedSeconds.value = Number(saved.elapsedSeconds) || 0
      lessonStatus.value = saved.lessonStatus || SESSION_STATUS.ACTIVE
      memory.value = { ...emptyMemory(), ...(saved.memory || {}) }
    } else {
      currentStage.value = stages[0]
      visitedStages.value = [stages[0]]
      completedStages.value = []
      startedAt.value = new Date().toISOString()
      elapsedSeconds.value = 0
      lessonStatus.value = SESSION_STATUS.ACTIVE
      memory.value = emptyMemory()
    }

    markVisited(currentStage.value)
    dirty.value = lessonStatus.value === SESSION_STATUS.ACTIVE
    startTicker()
    persist()
  }

  function goToStage(stage) {
    if (!stages.includes(stage)) return false
    const idx = stages.indexOf(stage)
    const cur = stageIndex.value
    // Allow revisit completed/visited or move to next only (no skipping ahead).
    if (idx > cur + 1 && !completedStages.value.includes(stages[idx - 1])) {
      return false
    }
    if (idx > cur) {
      markCompleted(stages[cur])
    }
    currentStage.value = stage
    markVisited(stage)
    dirty.value = true
    persist()
    return true
  }

  function next() {
    if (!canGoNext.value) return false
    return goToStage(stages[stageIndex.value + 1])
  }

  function back() {
    if (!canGoBack.value) return false
    return goToStage(stages[stageIndex.value - 1])
  }

  function continueForward() {
    return next()
  }

  function completeSession() {
    markCompleted(currentStage.value)
    for (const s of stages) markCompleted(s)
    currentStage.value = 'COMPLETE'
    markVisited('COMPLETE')
    lessonStatus.value = SESSION_STATUS.COMPLETED
    dirty.value = false
    persist()
    stopTicker()
  }

  function setAnswer(key, value) {
    memory.value = {
      ...memory.value,
      answers: { ...memory.value.answers, [key]: value },
    }
    dirty.value = true
    persist()
  }

  function setNotes(notes) {
    memory.value = { ...memory.value, notes: String(notes || '') }
    dirty.value = true
    persist()
  }

  function setTeacherContext(ctx) {
    memory.value = {
      ...memory.value,
      teacherContext: { ...memory.value.teacherContext, ...(ctx || {}) },
    }
    persist()
  }

  function clearRuntime() {
    stopTicker()
    writeStorage(null)
    lessonId.value = null
    currentStage.value = stages[0]
    visitedStages.value = []
    completedStages.value = []
    startedAt.value = null
    elapsedSeconds.value = 0
    lessonStatus.value = SESSION_STATUS.IDLE
    memory.value = emptyMemory()
    dirty.value = false
    teacherVoiceState.value = SESSION_VOICE_STATES.IDLE
    listeningState.value = false
    speakingState.value = false
    microphoneReady.value = false
  }

  function estimatedRemainingMinutes(totalEstimated) {
    const total = Math.max(1, Number(totalEstimated) || 18)
    const elapsedMin = elapsedSeconds.value / 60
    const frac = (stageIndex.value + 1) / totalStages.value
    const remaining = Math.max(1, Math.ceil(total * (1 - frac * 0.85) - elapsedMin * 0.2))
    return remaining
  }

  watch(currentStage, () => persist())

  onScopeDispose(() => {
    stopTicker()
  })

  return {
    stages,
    lessonId,
    currentStage,
    visitedStages,
    completedStages,
    startedAt,
    elapsedSeconds,
    lessonStatus,
    memory,
    dirty,
    teacherVoiceState,
    listeningState,
    speakingState,
    microphoneReady,
    stageIndex,
    totalStages,
    progressPercent,
    canGoBack,
    canGoNext,
    isLastStage,
    isComplete,
    bindLesson,
    goToStage,
    next,
    back,
    continueForward,
    completeSession,
    setAnswer,
    setNotes,
    setTeacherContext,
    clearRuntime,
    persist,
    estimatedRemainingMinutes,
  }
}
