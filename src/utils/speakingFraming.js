/**
 * Phase 1 product framing helpers.
 * Display-only remaps for early Alex-branded mission copy.
 * Does not change APIs, routing, or runtime ownership.
 */

const ALEX_FRAMED_TITLES = new Set([
  'speak with alex',
  'talk with alex',
  'practice with alex',
])

const INSTRUCTION_REWRITES = [
  [
    /^Have a natural conversation with Alex and use (.+)\.$/i,
    'Practise using $1 in today\'s lesson.',
  ],
  [
    /^Have a natural conversation with Alex using today's focus\.$/i,
    'Use today\'s focus in a natural conversation for this lesson.',
  ],
]

/**
 * Prefer story / package lesson title; never surface Alex-framed mission titles.
 * @param {string|null|undefined} rawTitle
 * @param {string|null|undefined} storyOrLessonTitle
 * @param {(key: string) => string} t
 */
export function educationalMissionTitle(rawTitle, storyOrLessonTitle, t) {
  const raw = String(rawTitle || '').trim()
  const story = String(storyOrLessonTitle || '').trim()
  const alexFramed = raw && ALEX_FRAMED_TITLES.has(raw.toLowerCase())

  if (story && (!raw || alexFramed)) {
    return story
  }
  if (alexFramed || !raw) {
    return t('student.languages.speakingJourney.framing.todaysSpeakingLesson')
  }
  return raw
}

/**
 * Soften stored planner instructions that name Alex before live continuation.
 * @param {string|null|undefined} raw
 */
export function educationalMissionInstructions(raw) {
  const text = String(raw || '').trim()
  if (!text) return ''
  for (const [pattern, replacement] of INSTRUCTION_REWRITES) {
    if (pattern.test(text)) {
      return text.replace(pattern, replacement)
    }
  }
  return text
}
