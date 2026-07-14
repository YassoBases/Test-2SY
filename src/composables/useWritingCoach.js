import { computed } from 'vue'

/**
 * Render-only coach panel from W7 draft response — never computes scores.
 */
export function useWritingCoach(lastTurn) {
  const revisionPlan = computed(() => lastTurn.value?.revision_plan || null)
  const feedback = computed(() => lastTurn.value?.feedback || null)
  const readyToComplete = computed(() => Boolean(lastTurn.value?.ready_to_complete))
  const hasCoach = computed(() => Boolean(revisionPlan.value || feedback.value))

  const encouragement = computed(() => revisionPlan.value?.encouragement || feedback.value?.encouragement || '')
  const mainIssue = computed(() => revisionPlan.value?.main_issue || feedback.value?.main_weakness || '')
  const whyItMatters = computed(() => revisionPlan.value?.why_it_matters || revisionPlan.value?.priority_fix || '')
  const mission = computed(() => revisionPlan.value?.revision_mission || '')
  const beforeExample = computed(() => revisionPlan.value?.before_example || '')
  const afterExample = computed(() => revisionPlan.value?.after_example || '')
  const guidanceSource = computed(() => revisionPlan.value?.guidance_source || '')
  const priorityKey = computed(() => revisionPlan.value?.priority_key || '')
  const nextLesson = computed(() => revisionPlan.value?.next_lesson_recommendation || feedback.value?.next_focus || '')
  const whatImproved = computed(() => {
    const fromPlan = revisionPlan.value?.what_improved
    const fromFeedback = feedback.value?.what_improved
    return fromPlan?.length ? fromPlan : (fromFeedback || [])
  })

  return {
    revisionPlan,
    feedback,
    readyToComplete,
    hasCoach,
    encouragement,
    mainIssue,
    whyItMatters,
    mission,
    beforeExample,
    afterExample,
    guidanceSource,
    priorityKey,
    nextLesson,
    whatImproved,
  }
}
