/**
 * Re-stage GrammarLessonOut into micro teaching cards (frontend only).
 * Grammar Engine / lesson package remain the source of truth.
 */

function splitIntoBeats(text, maxLen = 180) {
  const raw = String(text || '').trim()
  if (!raw) return []
  const parts = raw
    .split(/(?<=[.!?])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean)
  const beats = []
  for (const part of parts) {
    if (part.length <= maxLen) {
      beats.push(part)
      continue
    }
    let rest = part
    while (rest.length > maxLen) {
      let cut = rest.lastIndexOf(' ', maxLen)
      if (cut < 40) cut = maxLen
      beats.push(rest.slice(0, cut).trim())
      rest = rest.slice(cut).trim()
    }
    if (rest) beats.push(rest)
  }
  return beats
}

/**
 * @param {object} lesson GrammarLessonOut-like
 * @returns {Array<object>}
 */
export function buildTeachingCards(lesson) {
  const L = lesson || {}
  const cards = []
  let i = 0

  const openingBeats = splitIntoBeats(L.teacher_opening)
  if (openingBeats.length) {
    cards.push({
      id: `concept-${i++}`,
      kind: 'concept',
      titleKey: 'student.grammarTeacher.cards.concept',
      body: openingBeats[0],
      teacherLine: 'Here’s the main idea — keep it simple.',
      mood: 'calm',
    })
    for (let b = 1; b < openingBeats.length; b += 1) {
      cards.push({
        id: `explain-${i++}`,
        kind: 'explanation',
        titleKey: 'student.grammarTeacher.cards.explanation',
        body: openingBeats[b],
        teacherLine: 'Let me explain a little more.',
        mood: 'encouraging',
      })
    }
  }

  if (L.warmup) {
    cards.push({
      id: `warmup-${i++}`,
      kind: 'example',
      titleKey: 'student.grammarTeacher.cards.example',
      body: L.warmup,
      example: L.warmup,
      teacherLine: 'Try this small warm-up example with me.',
      mood: 'curious',
    })
  }

  const patterns = Array.isArray(L.expected_patterns) ? L.expected_patterns : []
  for (const pattern of patterns.slice(0, 4)) {
    cards.push({
      id: `pattern-${i++}`,
      kind: 'example',
      titleKey: 'student.grammarTeacher.cards.pattern',
      body: pattern,
      example: pattern,
      teacherLine: 'Notice this pattern — you’ll use it a lot.',
      mood: 'curious',
    })
  }

  const mistakes = Array.isArray(L.common_mistakes) ? L.common_mistakes : []
  for (const m of mistakes.slice(0, 3)) {
    cards.push({
      id: `checkpoint-${i++}`,
      kind: 'checkpoint',
      titleKey: 'student.grammarTeacher.cards.checkpoint',
      body: '',
      incorrect: m.incorrect,
      correct: m.correct,
      teacherLine: 'Quick checkpoint — spot the better sentence.',
      mood: 'encouraging',
    })
  }

  if (!cards.length) {
    cards.push({
      id: 'fallback-0',
      kind: 'concept',
      titleKey: 'student.grammarTeacher.cards.concept',
      body: L.lesson_goal || L.grammar_target || 'Let’s learn today’s grammar together.',
      teacherLine: 'We’ll take this one small step at a time.',
      mood: 'calm',
    })
  }

  return cards
}
