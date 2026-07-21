/**
 * AI Grammar Session V3 — stage contract (frontend runtime only).
 * Independent stages; only one active at a time.
 */

export const GRAMMAR_SESSION_STAGES = Object.freeze([
  'WELCOME',
  'MISSION',
  'LEARN',
  'PRACTICE',
  'SPEAKING',
  'WRITING',
  'REFLECTION',
  'COMPLETE',
])

export const GRAMMAR_SESSION_STAGE_META = Object.freeze({
  WELCOME: { labelKey: 'student.grammarSession.stages.welcome', icon: 'mdi-hand-wave' },
  MISSION: { labelKey: 'student.grammarSession.stages.mission', icon: 'mdi-flag-outline' },
  LEARN: { labelKey: 'student.grammarSession.stages.learn', icon: 'mdi-school-outline' },
  PRACTICE: { labelKey: 'student.grammarSession.stages.practice', icon: 'mdi-pencil-outline' },
  SPEAKING: { labelKey: 'student.grammarSession.stages.speaking', icon: 'mdi-microphone-outline' },
  WRITING: { labelKey: 'student.grammarSession.stages.writing', icon: 'mdi-fountain-pen-tip' },
  REFLECTION: { labelKey: 'student.grammarSession.stages.reflection', icon: 'mdi-lightbulb-on-outline' },
  COMPLETE: { labelKey: 'student.grammarSession.stages.complete', icon: 'mdi-check-decagram' },
})

/** Voice modality placeholders — not implemented in P0. */
export const SESSION_VOICE_STATES = Object.freeze({
  IDLE: 'idle',
  TEACHER_SPEAKING: 'teacher_speaking',
  LISTENING: 'listening',
  STUDENT_SPEAKING: 'student_speaking',
})

export const SESSION_STATUS = Object.freeze({
  IDLE: 'idle',
  ACTIVE: 'active',
  COMPLETED: 'completed',
})
