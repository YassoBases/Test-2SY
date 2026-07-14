/** Canonical writing learning goals — mirrors backend WritingGoal enum. */
export const WRITING_LEARNING_GOALS = [
  { id: 'general_english', icon: 'mdi-earth', labelKey: 'student.languages.writingJourney.goals.general_english', descKey: 'student.languages.writingJourney.goalsDesc.general_english' },
  { id: 'travel', icon: 'mdi-airplane', labelKey: 'student.languages.writingJourney.goals.travel', descKey: 'student.languages.writingJourney.goalsDesc.travel' },
  { id: 'business', icon: 'mdi-briefcase-outline', labelKey: 'student.languages.writingJourney.goals.business', descKey: 'student.languages.writingJourney.goalsDesc.business' },
  { id: 'ielts', icon: 'mdi-certificate-outline', labelKey: 'student.languages.writingJourney.goals.ielts', descKey: 'student.languages.writingJourney.goalsDesc.ielts' },
  { id: 'academic', icon: 'mdi-school-outline', labelKey: 'student.languages.writingJourney.goals.academic', descKey: 'student.languages.writingJourney.goalsDesc.academic' },
  { id: 'job_interview', icon: 'mdi-account-tie', labelKey: 'student.languages.writingJourney.goals.job_interview', descKey: 'student.languages.writingJourney.goalsDesc.job_interview' },
  { id: 'daily_communication', icon: 'mdi-message-text-outline', labelKey: 'student.languages.writingJourney.goals.daily_communication', descKey: 'student.languages.writingJourney.goalsDesc.daily_communication' },
  { id: 'creative_writing', icon: 'mdi-feather', labelKey: 'student.languages.writingJourney.goals.creative_writing', descKey: 'student.languages.writingJourney.goalsDesc.creative_writing' },
]

export function goalMemoryTokens(goalId) {
  const goal = WRITING_LEARNING_GOALS.find((g) => g.id === goalId)
  if (!goal) return [goalId]
  return [goalId.replace(/_/g, ' '), goalId]
}
