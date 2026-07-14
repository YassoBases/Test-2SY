/** Canonical listening learning goals — mirrors backend LearningGoal enum. */
export const LISTENING_LEARNING_GOALS = [
  { id: 'general_english', icon: 'mdi-earth', labelKey: 'student.languages.listeningJourney.goals.general_english', descKey: 'student.languages.coach.ux.goals.cards.general_english' },
  { id: 'daily_life', icon: 'mdi-home-outline', labelKey: 'student.languages.listeningJourney.goals.daily_life', descKey: 'student.languages.coach.ux.goals.cards.daily_life' },
  { id: 'conversation', icon: 'mdi-forum-outline', labelKey: 'student.languages.listeningJourney.goals.conversation', descKey: 'student.languages.coach.ux.goals.cards.conversation' },
  { id: 'travel', icon: 'mdi-airplane', labelKey: 'student.languages.listeningJourney.goals.travel', descKey: 'student.languages.coach.ux.goals.cards.travel' },
  { id: 'business', icon: 'mdi-briefcase-outline', labelKey: 'student.languages.listeningJourney.goals.business', descKey: 'student.languages.coach.ux.goals.cards.business' },
  { id: 'job_interview', icon: 'mdi-account-tie', labelKey: 'student.languages.listeningJourney.goals.job_interview', descKey: 'student.languages.coach.ux.goals.cards.job_interview' },
  { id: 'academic', icon: 'mdi-school-outline', labelKey: 'student.languages.listeningJourney.goals.academic', descKey: 'student.languages.coach.ux.goals.cards.academic' },
  { id: 'university', icon: 'mdi-bank-outline', labelKey: 'student.languages.listeningJourney.goals.university', descKey: 'student.languages.coach.ux.goals.cards.university' },
  { id: 'ielts', icon: 'mdi-certificate-outline', labelKey: 'student.languages.listeningJourney.goals.ielts', descKey: 'student.languages.coach.ux.goals.cards.ielts' },
  { id: 'toefl', icon: 'mdi-certificate', labelKey: 'student.languages.listeningJourney.goals.toefl', descKey: 'student.languages.coach.ux.goals.cards.toefl' },
]

/** Goal alias strings stored in learner memory — parsed server-side. */
export function goalMemoryTokens(goalId) {
  const goal = LISTENING_LEARNING_GOALS.find((g) => g.id === goalId)
  if (!goal) return []
  return [goalId.replace(/_/g, ' '), goalId]
}

export const READINESS_BANDS = [
  { key: 'NOT_READY', min: 0 },
  { key: 'ALMOST_READY', min: 50 },
  { key: 'READY', min: 80 },
  { key: 'PROMOTION_AVAILABLE', min: 100 },
]

export const JOURNEY_DIMENSIONS = [
  'learning_stage',
  'stage_score',
  'transition_gate',
  'confidence',
  'evidence',
  'objective_mastery',
  'challenge_stability',
  'consistency',
  'review_completion',
  'lesson_exposure',
]
