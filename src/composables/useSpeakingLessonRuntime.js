import { computed, ref } from 'vue'
import {
  advanceSpeakingLessonRuntime,
  fetchActiveSpeakingLessonRuntime,
  markSpeakingLessonBlockViewed,
  markSpeakingLessonMiniPrepComplete,
  markSpeakingLessonVocabViewed,
  openSpeakingLessonRuntime,
} from '../api/speakingLessonRuntime.js'

function applyView(target, data) {
  if (data?.state?.status === 'idle' || (data?.state && !data.state.package_id)) {
    target.value = null
    return
  }
  target.value = data || null
}

export function useSpeakingLessonRuntime() {
  const view = ref(null)
  const loading = ref(false)
  const advancing = ref(false)
  const error = ref('')

  const state = computed(() => view.value?.state || null)
  const packageData = computed(() => view.value?.package || null)
  const constraintsSummary = computed(() => view.value?.constraints_summary || {})
  const sectionProgress = computed(() => view.value?.section_progress || {})
  const currentSection = computed(() => state.value?.current_section || 'not_started')
  const readyForDiscussion = computed(() => Boolean(state.value?.ready_for_discussion))
  const hasActiveLesson = computed(() => Boolean(view.value?.package && state.value?.package_id))

  async function openLesson({ packageId, forceRestart } = {}) {
    loading.value = true
    error.value = ''
    try {
      const data = await openSpeakingLessonRuntime({ packageId, forceRestart })
      applyView(view, data)
      return data
    } catch (err) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to open lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadActive() {
    loading.value = true
    error.value = ''
    try {
      const data = await fetchActiveSpeakingLessonRuntime()
      applyView(view, data)
      return data
    } catch (err) {
      const status = err?.response?.status
      if (status === 404) {
        view.value = null
        error.value = ''
        return null
      }
      error.value = err?.response?.data?.detail || err?.message || 'Failed to load lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function advance() {
    advancing.value = true
    error.value = ''
    try {
      const data = await advanceSpeakingLessonRuntime()
      applyView(view, data)
      return data
    } catch (err) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to advance'
      throw err
    } finally {
      advancing.value = false
    }
  }

  async function markVocab(vocabularyId) {
    const data = await markSpeakingLessonVocabViewed(vocabularyId)
    applyView(view, data)
    return data
  }

  async function markBlock(blockId) {
    const data = await markSpeakingLessonBlockViewed(blockId)
    applyView(view, data)
    return data
  }

  async function completeMiniPrep() {
    const data = await markSpeakingLessonMiniPrepComplete()
    applyView(view, data)
    return data
  }

  function clear() {
    view.value = null
    error.value = ''
  }

  function hydrate(data) {
    applyView(view, data)
    error.value = ''
  }

  return {
    view,
    loading,
    advancing,
    error,
    state,
    packageData,
    constraintsSummary,
    sectionProgress,
    currentSection,
    readyForDiscussion,
    hasActiveLesson,
    openLesson,
    loadActive,
    advance,
    markVocab,
    markBlock,
    completeMiniPrep,
    hydrate,
    clear,
  }
}
