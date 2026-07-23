/**
 * Client-side session for the generate-only Grammar lesson package.
 * Survives refresh; no backend persistence required.
 */
import { computed, ref } from 'vue'

export const CURRENT_GRAMMAR_METHODOLOGY_VERSION = 'grammar_lesson_methodology_v2_arabic_first'

const STORAGE_KEY = 'edumind.grammar.activeLesson.v2'
const LEGACY_STORAGE_KEYS = ['edumind.grammar.activeLesson.v1']

const activeLesson = ref(null)
let hydrated = false

function parseMaybeJson(value) {
  if (!value || typeof value !== 'string') return value
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[_()[\]{}+./:;!?'"`-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function hasArabic(value) {
  return /[\u0600-\u06ff]/.test(String(value || ''))
}

function collectText(value) {
  if (!value) return ''
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.map(collectText).join(' ')
  if (typeof value === 'object') return Object.values(value).map(collectText).join(' ')
  return String(value)
}

function isGenericFiller(value, lesson) {
  const text = normalizeText(collectText(value))
  if (!text) return false
  const displayName = normalizeText(lesson?.display_name || lesson?.lesson_title || '')
  const grammarId = normalizeText(lesson?.grammar_id || lesson?.grammar_target || '')
  const topicNames = [displayName, grammarId].filter(Boolean)
  const genericNeedles = [
    'welcome today we focus on',
    'today you will learn',
    'use this grammar for communication',
    'this grammar is useful',
    'focus on the meaning',
    'use this pattern for',
    'subject verb',
    'this sentence shows',
    'example with',
  ]
  if (genericNeedles.some((needle) => text.includes(needle))) return true
  return topicNames.some((name) =>
    [
      `i use ${name}`,
      `she uses ${name}`,
      `they practice ${name}`,
      `use this pattern for ${name}`,
      `today we focus on ${name}`,
      `i ${name}`,
      `she ${name}`,
      `they ${name}`,
    ].some((needle) => text.includes(needle)),
  )
}

function methodologyIsCurrent(lesson) {
  return lesson?.methodology_version === CURRENT_GRAMMAR_METHODOLOGY_VERSION
}

function generationIsAuthored(lesson) {
  const mode = normalizeText(lesson?.generation_mode || '')
  return lesson?.authoring_status !== 'retry_required' && !/^(temporary|fallback|retry required)/.test(mode)
}

function validExplainedExamples(content, lesson) {
  const examples = Array.isArray(content?.model_examples) ? content.model_examples : []
  return (
    examples.length >= 3 &&
    examples.length <= 5 &&
    examples.every((example) => {
      const sentence = String(example?.sentence || '').trim()
      const targetForm = String(example?.target_form || '').trim()
      const explanation = String(example?.arabic_explanation || '').trim()
      return sentence && targetForm && hasArabic(explanation) && !isGenericFiller(sentence, lesson)
    })
  )
}

function validConcept(content, lesson) {
  const explanation = content?.concept_explanation
  const clarification = content?.arabic_clarification || {}
  const text = collectText([
    explanation?.arabic_concept_intro,
    explanation?.arabic_concept_introduction,
    clarification?.arabic,
    clarification?.arabic_speaker_warning,
    clarification?.arabic_english_contrast,
  ])
  const cefr = String(lesson?.cefr_level || '').toUpperCase()
  const minimumArabic = cefr === 'A1' || cefr === 'A2' ? 80 : 20
  const arabicChars = (text.match(/[\u0600-\u06ff]/g) || []).length
  return arabicChars >= minimumArabic && !isGenericFiller(explanation, lesson)
}

function validRulesAndMistakes(content, lesson) {
  const form = content?.form_and_rules || {}
  const patterns = Array.isArray(form.patterns) ? form.patterns : []
  const useCases = Array.isArray(form.use_cases) ? form.use_cases : []
  const visualSummary = Array.isArray(form.visual_summary) ? form.visual_summary : []
  const mistakes = Array.isArray(content?.contrasts_and_mistakes) ? content.contrasts_and_mistakes : []
  return (
    patterns.length >= 1 &&
    patterns.length <= 4 &&
    patterns.every((item) => item?.explanation && item?.example && !isGenericFiller(item, lesson)) &&
    useCases.length > 0 &&
    visualSummary.length > 0 &&
    mistakes.length >= 2 &&
    mistakes.length <= maxMistakeCount(lesson) &&
    mistakes.every((item) => item?.incorrect && item?.correct && hasArabic(item?.why) && item?.misunderstanding)
  )
}

function maxMistakeCount(lesson) {
  const grammarId = String(lesson?.grammar_id || lesson?.grammar_target || '').trim()
  return grammarId === 'gram_be_present' ? 6 : 4
}

function validPractice(content, lesson) {
  const understanding = Array.isArray(content?.understanding_checks) ? content.understanding_checks : []
  const guided = Array.isArray(content?.guided_practice) ? content.guided_practice : []
  const supported = Array.isArray(content?.supported_production) ? content.supported_production : []
  const maxGuided = String(lesson?.grammar_id || lesson?.grammar_target || '').trim() === 'gram_be_present' ? 12 : 6
  return (
    understanding.length >= 2 &&
    understanding.length <= 3 &&
    guided.length >= 4 &&
    guided.length <= maxGuided &&
    supported.length >= 1 &&
    content?.transfer?.type === 'transfer' &&
    content?.exit_check?.recognition &&
    content?.exit_check?.correction &&
    content?.exit_check?.production &&
    !isGenericFiller([understanding, guided, supported, content.transfer, content.exit_check], lesson)
  )
}

export function hasCanonicalGrammarLessonContent(lesson) {
  const raw = lesson?.student_content
  const content = raw && typeof raw === 'object' ? raw : parseMaybeJson(raw)
  return !!(
    methodologyIsCurrent(lesson) &&
    generationIsAuthored(lesson) &&
    content &&
    typeof content === 'object' &&
    content.orientation &&
    content.meaning_hook &&
    validConcept(content, lesson) &&
    validExplainedExamples(content, lesson) &&
    validRulesAndMistakes(content, lesson) &&
    validPractice(content, lesson) &&
    content.exit_check &&
    content.reflection &&
    !isGenericFiller(content, lesson)
  )
}

function readStorage() {
  try {
    for (const key of LEGACY_STORAGE_KEYS) sessionStorage.removeItem(key)
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object' || !parsed.lesson_id) {
      sessionStorage.removeItem(STORAGE_KEY)
      return null
    }
    if (!hasCanonicalGrammarLessonContent(parsed)) {
      sessionStorage.removeItem(STORAGE_KEY)
      return null
    }
    return parsed
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
    return null
  }
}

function writeStorage(lesson) {
  try {
    if (!lesson) {
      sessionStorage.removeItem(STORAGE_KEY)
      return
    }
    if (!hasCanonicalGrammarLessonContent(lesson)) {
      sessionStorage.removeItem(STORAGE_KEY)
      return
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(lesson))
  } catch {
    /* ignore quota / private mode */
  }
}

export function useGrammarLessonSession() {
  if (!hydrated) {
    activeLesson.value = readStorage()
    hydrated = true
  }

  const hasActiveLesson = computed(() => !!activeLesson.value?.lesson_id)

  function saveLesson(lesson) {
    activeLesson.value = lesson && hasCanonicalGrammarLessonContent(lesson) ? lesson : null
    writeStorage(activeLesson.value)
  }

  function clearLesson() {
    activeLesson.value = null
    writeStorage(null)
  }

  function hydrate() {
    activeLesson.value = readStorage()
    return activeLesson.value
  }

  return {
    activeLesson,
    hasActiveLesson,
    saveLesson,
    clearLesson,
    hydrate,
  }
}
