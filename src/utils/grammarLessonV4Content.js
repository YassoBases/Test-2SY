/**
 * Frontend-only content shaping for Grammar Lesson V4.
 * GrammarLessonOut remains the source of truth — no engine writes.
 */

function clean(text) {
  return String(text || '').trim()
}

export function buildEnglishExplanation(lesson) {
  const L = lesson || {}
  const opening = clean(L.teacher_opening)
  const goal = clean(L.lesson_goal)
  const hints = Array.isArray(L.teacher_hints) ? L.teacher_hints.filter(Boolean) : []
  const mistakes = Array.isArray(L.common_mistakes) ? L.common_mistakes : []
  const patterns = Array.isArray(L.expected_patterns) ? L.expected_patterns.filter(Boolean) : []

  const paragraphs = []
  if (opening) {
    paragraphs.push({ key: 'what', titleKey: 'student.grammarV4.explain.what', body: opening })
  }
  if (goal) {
    paragraphs.push({
      key: 'why',
      titleKey: 'student.grammarV4.explain.why',
      body: goal,
    })
  }
  if (patterns.length) {
    paragraphs.push({
      key: 'structure',
      titleKey: 'student.grammarV4.explain.structure',
      body: patterns.join('\n'),
      list: patterns,
    })
  }
  if (hints.length) {
    paragraphs.push({
      key: 'rules',
      titleKey: 'student.grammarV4.explain.rules',
      body: hints.join('\n'),
      list: hints,
    })
  }
  if (mistakes.length) {
    paragraphs.push({
      key: 'mistakes',
      titleKey: 'student.grammarV4.explain.mistakes',
      body: '',
      mistakes,
    })
  }
  if (L.warmup) {
    paragraphs.push({
      key: 'when',
      titleKey: 'student.grammarV4.explain.when',
      body: clean(L.warmup),
    })
  }
  return paragraphs
}

export function buildSeedExamples(lesson) {
  const L = lesson || {}
  const groups = {
    easy: [],
    daily: [],
    school: [],
    university: [],
    work: [],
    travel: [],
    mistakes: [],
  }

  const patterns = Array.isArray(L.expected_patterns) ? L.expected_patterns : []
  patterns.forEach((p, i) => {
    const bucket = i % 2 === 0 ? 'easy' : 'daily'
    groups[bucket].push({
      id: `pat-${i}`,
      en: p,
      ar: '',
      explanation: 'Pattern from today’s lesson.',
      category: bucket,
    })
  })

  if (L.warmup) {
    groups.daily.push({
      id: 'warmup-0',
      en: clean(L.warmup),
      ar: '',
      explanation: 'Warm-up example from your lesson.',
      category: 'daily',
    })
  }

  if (L.main_activity) {
    groups.school.push({
      id: 'main-0',
      en: clean(L.main_activity),
      ar: '',
      explanation: 'Practice idea from the main activity.',
      category: 'school',
    })
  }

  const mistakes = Array.isArray(L.common_mistakes) ? L.common_mistakes : []
  mistakes.forEach((m, i) => {
    groups.mistakes.push({
      id: `mis-${i}`,
      en: `${m.incorrect} → ${m.correct}`,
      ar: '',
      explanation: 'Compare the incorrect form with the corrected sentence.',
      category: 'mistakes',
      incorrect: m.incorrect,
      correct: m.correct,
    })
  })

  // Ensure every category has at least a gentle placeholder derived from topic.
  const topic = L.grammar_target || L.lesson_title || 'this grammar'
  const fillers = [
    ['easy', `Simple: I use ${topic} in a short sentence.`],
    ['daily', `Daily life: I need ${topic} when I talk with friends.`],
    ['school', `School: In class, we practice ${topic}.`],
    ['university', `University: Students use ${topic} in presentations.`],
    ['work', `Work: At work, ${topic} helps you sound clear.`],
    ['travel', `Travel: When traveling, ${topic} helps you ask for help.`],
  ]
  for (const [cat, en] of fillers) {
    if (!groups[cat].length) {
      groups[cat].push({
        id: `fill-${cat}`,
        en,
        ar: '',
        explanation: `Contextual example for ${topic}.`,
        category: cat,
        seeded: true,
      })
    }
  }

  return groups
}

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/**
 * Build ≥15 adaptive practice items from the lesson package.
 */
export function buildPracticeQuestions(lesson, { minCount = 15 } = {}) {
  const L = lesson || {}
  const patterns = (L.expected_patterns || []).filter(Boolean)
  const mistakes = L.common_mistakes || []
  const followUps = (L.follow_up_questions || []).filter(Boolean)
  const topic = L.grammar_target || 'grammar'
  const items = []
  let id = 0

  const push = (q) => {
    items.push({ ...q, id: `q-${id++}`, difficulty: q.difficulty || 'easy' })
  }

  // Easy MCQ from patterns
  patterns.forEach((p, i) => {
    const distractors = patterns.filter((x) => x !== p).slice(0, 2)
    while (distractors.length < 2) distractors.push(`Another form of ${topic}`)
    push({
      type: 'mcq',
      difficulty: i < 2 ? 'easy' : 'medium',
      prompt: `Which pattern matches today’s grammar (${topic})?`,
      options: shuffle([p, ...distractors.slice(0, 2), `Not related to ${topic}`]).slice(0, 4),
      answer: p,
      explanation: `“${p}” is an expected pattern for this lesson.`,
    })
  })

  // Fill blank
  patterns.slice(0, 4).forEach((p) => {
    const words = p.split(/\s+/).filter(Boolean)
    if (words.length < 2) return
    const blankAt = Math.min(1, words.length - 1)
    const answer = words[blankAt]
    const shown = words.map((w, i) => (i === blankAt ? '______' : w)).join(' ')
    push({
      type: 'fill',
      difficulty: 'easy',
      prompt: `Fill the blank: ${shown}`,
      answer,
      explanation: `The missing word is “${answer}”. Full pattern: ${p}`,
    })
  })

  // Sentence correction
  mistakes.forEach((m) => {
    push({
      type: 'correction',
      difficulty: 'medium',
      prompt: `Correct this sentence:\n${m.incorrect}`,
      answer: m.correct,
      explanation: `Incorrect: ${m.incorrect}\nCorrect: ${m.correct}`,
      mistakeWhy: 'This is a common mistake for today’s grammar.',
    })
  })

  // Translation-style (EN → short response using pattern)
  patterns.slice(0, 3).forEach((p) => {
    push({
      type: 'translation',
      difficulty: 'medium',
      prompt: `Write one English sentence that uses this idea:\n${p}`,
      answer: p,
      acceptContains: p.split(/\s+/).slice(0, 2).join(' ').toLowerCase(),
      explanation: `A strong answer uses the pattern: ${p}`,
    })
  })

  // Sentence building
  patterns.slice(0, 3).forEach((p) => {
    const tokens = shuffle(p.split(/\s+/).filter(Boolean))
    if (tokens.length < 2) return
    push({
      type: 'build',
      difficulty: 'hard',
      prompt: 'Build the sentence in the correct order:',
      tokens,
      answer: p,
      explanation: `Correct order: ${p}`,
    })
  })

  // Follow-up open prompts as translation/build hybrids
  followUps.forEach((q, i) => {
    push({
      type: 'translation',
      difficulty: i < 2 ? 'medium' : 'hard',
      prompt: q,
      answer: patterns[0] || topic,
      acceptContains: topic.toLowerCase().slice(0, 6),
      explanation: L.teacher_hints?.[0] || 'Use today’s grammar in your answer.',
    })
  })

  // Pad to minCount with progressive difficulty clones
  let pad = 0
  while (items.length < minCount) {
    const base = patterns[pad % Math.max(patterns.length, 1)] || topic
    push({
      type: 'mcq',
      difficulty: items.length < 8 ? 'easy' : items.length < 12 ? 'medium' : 'hard',
      prompt: `Choose the best option related to ${topic}:`,
      options: shuffle([
        base,
        `Ignore ${topic}`,
        `Never use ${topic}`,
        `Random words`,
      ]),
      answer: base,
      explanation: `Stay focused on ${topic}.`,
    })
    pad += 1
    if (pad > 40) break
  }

  // Sort easy → hard
  const rank = { easy: 0, medium: 1, hard: 2 }
  return items.sort((a, b) => (rank[a.difficulty] ?? 1) - (rank[b.difficulty] ?? 1))
}

/** Soft off-topic filter for lesson-scoped chat (frontend guard). */
export function isLikelyOffTopic(message, lesson) {
  const text = clean(message).toLowerCase()
  if (!text) return true
  const topic = clean(lesson?.grammar_target || '').toLowerCase()
  const allowHints = [
    'grammar',
    'example',
    'explain',
    'arabic',
    'english',
    'mistake',
    'rule',
    'sentence',
    'correct',
    'why',
    'how',
    'meaning',
    'translate',
    'تمرين',
    'قاعدة',
    'مثال',
    'اشرح',
    'عربي',
    topic,
  ].filter(Boolean)

  const blockHints = [
    'python',
    'javascript',
    'code',
    'joke',
    'networking',
    'bitcoin',
    'homework math',
    'write a poem about',
  ]
  if (blockHints.some((b) => text.includes(b))) return true
  if (allowHints.some((h) => h && text.includes(h))) return false
  // Short follow-ups are allowed in-thread
  if (text.length < 80) return false
  return false
}

export function parseExamplesFromTutorText(text, category = 'daily') {
  const lines = String(text || '')
    .split(/\n+/)
    .map((l) => l.replace(/^[-*\d.)\s]+/, '').trim())
    .filter((l) => l.length > 3 && l.length < 220)
  return lines.slice(0, 8).map((en, i) => ({
    id: `gen-${category}-${Date.now()}-${i}`,
    en,
    ar: '',
    explanation: 'Generated for today’s grammar lesson.',
    category,
  }))
}
