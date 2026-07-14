import { computed } from 'vue'

/**
 * Render-only evaluation panel from W7 draft response — never computes scores.
 */
export function useWritingEvaluation(lastTurn) {
  const evaluation = computed(() => lastTurn.value?.evaluation_display || null)
  const lessonProgress = computed(() => lastTurn.value?.lesson_progress || null)
  const hasEvaluation = computed(() => Boolean(evaluation.value))
  const readyToComplete = computed(() => Boolean(lastTurn.value?.ready_to_complete))

  const dimensions = computed(() => evaluation.value?.dimensions || [])
  const successCriteria = computed(() => evaluation.value?.success_criteria || [])
  const strengths = computed(() => evaluation.value?.strengths || [])
  const improvements = computed(() => evaluation.value?.improvements || [])

  const educationalAnalysis = computed(() => lastTurn.value?.educational_analysis || null)
  const hasEducationalAnalysis = computed(() => Boolean(educationalAnalysis.value?.available))

  return {
    evaluation,
    lessonProgress,
    hasEvaluation,
    readyToComplete,
    dimensions,
    successCriteria,
    strengths,
    improvements,
    educationalAnalysis,
    hasEducationalAnalysis,
  }
}
