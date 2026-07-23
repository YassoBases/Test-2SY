import { computed, ref } from 'vue'
import { fetchGrammarDashboard, startGrammarLesson } from '../api/grammar.js'
import { useGrammarModule } from './useGrammarModule.js'
import { useGrammarLessonSession } from './useGrammarLessonSession.js'

const FRIENDLY = {
  dashboard: "We couldn't load your Grammar home. Please try again.",
  generate: "We couldn't prepare your Grammar lesson. Please try again.",
  disabled: 'Grammar is not available right now.',
}

export function useGrammarHome() {
  const { isEnabled, isReady, loading: statusLoading, refresh } = useGrammarModule()
  const { activeLesson, hasActiveLesson, saveLesson, clearLesson, hydrate } = useGrammarLessonSession()

  const dashboard = ref(null)
  const dashboardLoading = ref(false)
  const generating = ref(false)
  const errorMessage = ref('')
  const viewingLesson = ref(false)

  const topicLabel = computed(() => {
    const t = dashboard.value?.current_grammar_topic
    return t?.display_name || dashboard.value?.grammar_target || ''
  })

  const hasPreview = computed(() => !!dashboard.value?.has_lesson_preview)
  const isEmpty = computed(
    () => !!dashboard.value?.enabled && !hasPreview.value && !hasActiveLesson.value,
  )

  async function bootstrap() {
    errorMessage.value = ''
    hydrate()
    if (hasActiveLesson.value) {
      viewingLesson.value = false
    }
    await refresh()
    if (!isEnabled.value) {
      dashboard.value = { enabled: false }
      return
    }
    await loadDashboard()
  }

  async function loadDashboard() {
    dashboardLoading.value = true
    errorMessage.value = ''
    try {
      dashboard.value = await fetchGrammarDashboard()
    } catch {
      errorMessage.value = FRIENDLY.dashboard
      dashboard.value = null
    } finally {
      dashboardLoading.value = false
    }
  }

  async function startLesson() {
    if (generating.value || !isEnabled.value) return
    generating.value = true
    errorMessage.value = ''
    try {
      const lesson = await startGrammarLesson({
        use_llm_authoring: true,
        grammar_id: dashboard.value?.grammar_target || undefined,
      })
      saveLesson(lesson)
      viewingLesson.value = true
    } catch {
      errorMessage.value = FRIENDLY.generate
    } finally {
      generating.value = false
    }
  }

  function continueLesson() {
    if (!hasActiveLesson.value) return
    errorMessage.value = ''
    viewingLesson.value = true
  }

  function finishLesson() {
    clearLesson()
    viewingLesson.value = false
    errorMessage.value = ''
    loadDashboard()
  }

  function backToHome() {
    viewingLesson.value = false
    errorMessage.value = ''
  }

  async function retry() {
    errorMessage.value = ''
    // Prefer regenerating when the home preview is already loaded.
    if (dashboard.value?.has_lesson_preview || viewingLesson.value || hasActiveLesson.value) {
      await startLesson()
      return
    }
    await loadDashboard()
  }

  return {
    isEnabled,
    isReady,
    statusLoading,
    dashboard,
    dashboardLoading,
    generating,
    errorMessage,
    viewingLesson,
    activeLesson,
    hasActiveLesson,
    topicLabel,
    hasPreview,
    isEmpty,
    friendlyDisabled: FRIENDLY.disabled,
    bootstrap,
    loadDashboard,
    startLesson,
    continueLesson,
    finishLesson,
    backToHome,
    retry,
  }
}
