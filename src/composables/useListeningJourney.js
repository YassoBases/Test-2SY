import { computed, ref } from 'vue'
import { fetchListeningJourney, updateLearnerMemory } from '../api/language.js'
import { useListeningPromotion } from './useListeningPromotion.js'
import { LISTENING_LEARNING_GOALS } from '../constants/listeningGoals.js'
import { getErrorMessage } from '../api/client.js'

let journeyCache = null
let journeyPromise = null

/**
 * Unified listening journey — canonical ListeningJourneyBundle + promotion test flows.
 */
export function useListeningJourney() {
  const promotion = useListeningPromotion()

  const journey = ref(null)
  const journeyLoading = ref(false)
  const journeyError = ref('')

  const savingGoal = ref(false)
  const goalSaved = ref(false)

  const officialCefr = computed(() => journey.value?.official_level || '—')
  const targetCefr = computed(() => journey.value?.journey_target?.level || '—')
  const targetLabel = computed(() => journey.value?.journey_target?.label || '—')
  const readinessBand = computed(() => journey.value?.promotion?.readiness_band || 'NOT_READY')
  const canStartTest = computed(() => Boolean(journey.value?.promotion?.can_start_test))
  const blockerItems = computed(() => journey.value?.promotion?.primary_blockers || [])
  const activeGoalId = computed(() => journey.value?.personal_goal?.id || 'general_english')
  const narrative = computed(() => journey.value?.narrative || null)
  const timelineSteps = computed(() => narrative.value?.timeline_steps || [])
  const historyEvents = computed(() => narrative.value?.history_events || [])
  const activeLessonId = computed(() => journey.value?.active_lesson?.lesson_id ?? null)
  const activeLessonLifecycle = computed(() => journey.value?.active_lesson?.lifecycle_state ?? null)

  async function loadJourneyBundle({ force = false } = {}) {
    if (!force && journeyCache) {
      journey.value = journeyCache
      return journeyCache
    }
    if (journeyPromise) return journeyPromise
    journeyLoading.value = true
    journeyError.value = ''
    journeyPromise = fetchListeningJourney()
      .then((data) => {
        journeyCache = data
        journey.value = data
        return data
      })
      .catch((err) => {
        journeyError.value = getErrorMessage(err, 'Could not load listening journey')
        throw err
      })
      .finally(() => {
        journeyLoading.value = false
        journeyPromise = null
      })
    return journeyPromise
  }

  async function loadJourney({ force = false } = {}) {
    await Promise.all([loadJourneyBundle({ force }), promotion.loadStatus({ force })])
  }

  async function refreshAfterPractice() {
    await loadJourney({ force: true })
  }

  async function selectGoal(goalId) {
    savingGoal.value = true
    goalSaved.value = false
    try {
      const label = LISTENING_LEARNING_GOALS.find((g) => g.id === goalId)?.id.replace(/_/g, ' ') || goalId
      await updateLearnerMemory({
        interests: [],
        learning_goals: [label],
      })
      goalSaved.value = true
      await loadJourney({ force: true })
    } finally {
      savingGoal.value = false
    }
  }

  return {
    ...promotion,
    journey,
    journeyLoading,
    journeyError,
    savingGoal,
    goalSaved,
    officialCefr,
    targetCefr,
    targetLabel,
    readinessBand,
    canStartTest,
    activeGoalId,
    blockerItems,
    narrative,
    timelineSteps,
    historyEvents,
    activeLessonId,
    activeLessonLifecycle,
    loadJourney,
    refreshAfterPractice,
    selectGoal,
  }
}
