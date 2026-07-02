/** Teacher personality — natural-language UI mapped to existing API fields. */

export const defaultTeacherAiProfile = {
  teacher_teaching_style: 'step_by_step',
  teacher_tone: 'balanced',
  teacher_question_style: 'mixed',
  teacher_motivation_level: 'medium',
  teacher_display_name: '',
  teacher_bio: '',
  teacher_signature_phrase: '',
}

export const TEACHER_BIO_MAX_LENGTH = 2000
export const TEACHER_SIGNATURE_MAX_LENGTH = 500

const EXAMPLE_ANSWER_PREFIX = 'مثال من شرحي: '

/** Legacy prefixes from earlier profile versions — merged on load. */
const LEGACY_LESSON_START_PREFIX = 'كيف أبدأ الدرس: '
const LEGACY_LESSON_END_PREFIX = 'كيف أنهي الدرس: '
const LEGACY_COMMUNICATION_PREFIX = 'تواصلي مع الطلاب: '
const LEGACY_HABIT_LINE_PREFIX = 'عاداتي: '

export function defaultTeacherAiEnums() {
  return {
    teacherTeachingStyle: defaultTeacherAiProfile.teacher_teaching_style,
    teacherQuestionStyle: defaultTeacherAiProfile.teacher_question_style,
    teacherTone: defaultTeacherAiProfile.teacher_tone,
    teacherMotivationLevel: defaultTeacherAiProfile.teacher_motivation_level,
  }
}

/** @deprecated Use defaultTeacherAiEnums — habits UI removed in 2.2 */
export function deriveEnumsFromHabits() {
  return defaultTeacherAiEnums()
}

export function buildTeacherBioPayload({ howYouExplain, exampleAnswer }) {
  const parts = []
  const core = (howYouExplain || '').trim()
  if (core) parts.push(core)
  const example = (exampleAnswer || '').trim()
  if (example) parts.push(`${EXAMPLE_ANSWER_PREFIX}${example}`)
  const payload = parts.join('\n\n')
  if (!payload) return null
  return payload.slice(0, TEACHER_BIO_MAX_LENGTH)
}

export function parseTeacherBioPayload(bio) {
  const text = bio || ''
  if (!text.trim()) {
    return { howYouExplain: '', exampleAnswer: '' }
  }

  const blocks = text.split(/\n\n+/)
  const narrative = []
  let exampleAnswer = ''

  for (const block of blocks) {
    const trimmed = block.trim()
    if (trimmed.startsWith(EXAMPLE_ANSWER_PREFIX)) {
      exampleAnswer = trimmed.slice(EXAMPLE_ANSWER_PREFIX.length).trim()
      continue
    }
    narrative.push(trimmed)
  }

  const howYouExplain = mergeLegacyStructuredLines(narrative.join('\n\n'))

  return {
    howYouExplain: howYouExplain.slice(0, TEACHER_BIO_MAX_LENGTH),
    exampleAnswer,
  }
}

function mergeLegacyStructuredLines(text) {
  if (!text.trim()) return ''

  const blocks = text.split(/\n\n+/)
  const narrative = []
  const legacy = []

  for (const block of blocks) {
    const trimmed = block.trim()
    if (
      trimmed.startsWith(LEGACY_LESSON_START_PREFIX) ||
      trimmed.startsWith(LEGACY_LESSON_END_PREFIX) ||
      trimmed.startsWith(LEGACY_COMMUNICATION_PREFIX) ||
      trimmed.startsWith(LEGACY_HABIT_LINE_PREFIX)
    ) {
      legacy.push(trimmed)
    } else {
      narrative.push(trimmed)
    }
  }

  const parts = [...narrative, ...legacy].filter(Boolean)
  return parts.join('\n\n')
}

export function parseSignaturePhrases(text) {
  if (!text?.trim()) return []
  return text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
}

export function serializeSignaturePhrases(phrases) {
  const joined = (phrases || [])
    .map((phrase) => phrase.trim())
    .filter(Boolean)
    .join('\n')
  if (!joined) return null
  return joined.slice(0, TEACHER_SIGNATURE_MAX_LENGTH)
}

export function labelForTeacherOption(options, value) {
  return options.find((o) => o.value === value)?.title || value
}

/** @deprecated Legacy exports kept for any remaining imports */
export const teacherNaturalHabitOptions = []
export const teacherTeachingStyleOptions = []
export const teacherToneOptions = []
export const teacherQuestionStyleOptions = []
export const teacherMotivationOptions = []
