import { computed, ref } from 'vue'
import { fetchWritingJourney, updateLearnerMemory } from '../api/language.js'
import { WRITING_LEARNING_GOALS, goalMemoryTokens } from '../constants/writingGoals.js'
import { getErrorMessage } from '../api/client.js'

/**
 * Writing journey — runtime bundle from GET /writing/journey.
 */
export function useWritingJourney() {
  const loading = ref(false)
  const error = ref('')
  const journey = ref(null)
  const savingGoal = ref(false)
  const goalSaved = ref(false)
  const lastSession = ref(null)

  const activeGoalId = computed(() => journey.value?.personal_goal?.id || 'travel')
  const activeGoalLabel = computed(() => journey.value?.personal_goal?.label || activeGoalId.value)
  const officialCefr = computed(() => journey.value?.official_writing_level || 'B1')
  const learningStageLabel = computed(() => journey.value?.learning_stage_label || '')
  const learningStage = computed(() => journey.value?.learning_stage ?? null)
  const readinessScore = computed(() => journey.value?.readiness_score ?? null)
  const readinessBand = computed(() => journey.value?.readiness_band || '')
  const canStartWpa = computed(() => Boolean(journey.value?.can_start_wpa))
  const primaryBlockers = computed(() => journey.value?.primary_blockers || [])
  const promotionTarget = computed(() => journey.value?.promotion_target || '')
  const progressSummary = computed(() => journey.value?.progress_summary || '')
  const nextMilestone = computed(() => journey.value?.next_milestone || '')
  const weakSkills = computed(() => journey.value?.weak_skills || [])
  const strongSkills = computed(() => journey.value?.strong_skills || [])
  const todaysMission = computed(() => journey.value?.todays_mission || null)
  const promotion = computed(() => journey.value?.promotion || null)
  const estimatedLessonsRemaining = computed(() => journey.value?.estimated_lessons_remaining ?? null)

  async function loadJourney() {
    loading.value = true
    error.value = ''
    try {
      journey.value = await fetchWritingJourney()
    } catch (err) {
      error.value = getErrorMessage(err, 'Could not load writing journey')
    } finally {
      loading.value = false
    }
  }

  async function selectGoal(goalId) {
    savingGoal.value = true
    goalSaved.value = false
    try {
      const tokens = goalMemoryTokens(goalId)
      await updateLearnerMemory({
        interests: [],
        learning_goals: tokens,
      })
      await loadJourney()
      goalSaved.value = true
    } finally {
      savingGoal.value = false
    }
  }

  function recordSession(summary) {
    lastSession.value = summary
  }

  return {
    loading,
    error,
    journey,
    activeGoalId,
    activeGoalLabel,
    officialCefr,
    learningStageLabel,
    learningStage,
    readinessScore,
    readinessBand,
    canStartWpa,
    primaryBlockers,
    promotionTarget,
    progressSummary,
    nextMilestone,
    weakSkills,
    strongSkills,
    todaysMission,
    promotion,
    estimatedLessonsRemaining,
    savingGoal,
    goalSaved,
    lastSession,
    loadJourney,
    selectGoal,
    recordSession,
  }
}
