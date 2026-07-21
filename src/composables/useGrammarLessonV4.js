/**
 * Grammar Lesson V4 — single-page orchestration (frontend only).
 * Uses GrammarLessonOut + existing Tutor APIs. No engine writes except finish via parent.
 */
import { computed, ref, watch } from 'vue'
import { getErrorMessage } from '../api/client.js'
import { postTutorTurn } from '../api/aiTutor.js'
import {
  buildEnglishExplanation,
  buildPracticeQuestions,
  buildSeedExamples,
  isLikelyOffTopic,
  parseExamplesFromTutorText,
} from '../utils/grammarLessonV4Content.js'

function speak(text, lang = 'en-US') {
  if (typeof window === 'undefined' || !window.speechSynthesis) return false
  try {
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(String(text || ''))
    u.lang = lang
    window.speechSynthesis.speak(u)
    return true
  } catch {
    return false
  }
}

export function useGrammarLessonV4(lessonRef) {
  const arabicExplanation = ref('')
  const arabicLoading = ref(false)
  const arabicError = ref('')

  const exampleGroups = ref(buildSeedExamples(lessonRef.value))
  const examplesLoading = ref(false)
  const examplesError = ref('')

  const chat = ref([])
  const chatDraft = ref('')
  const chatLoading = ref(false)
  const chatError = ref('')
  const conversationId = ref('')

  const practice = ref([])
  const practiceIndex = ref(0)
  const practiceAnswer = ref('')
  const practiceSelected = ref(null)
  const practiceBuild = ref([])
  const practiceRemaining = ref([])
  const practiceFeedback = ref(null)
  const practiceHistory = ref([])
  const remedialsLeft = ref(0)

  const summaryReady = ref(false)

  const lesson = computed(() => lessonRef.value || {})
  const englishBlocks = computed(() => buildEnglishExplanation(lesson.value))
  const topic = computed(() => lesson.value.grammar_target || lesson.value.lesson_title || '')
  const difficulty = computed(() => lesson.value.difficulty || 'guided')
  const minutes = computed(() => lesson.value.estimated_minutes ?? 18)

  const currentQuestion = computed(() => practice.value[practiceIndex.value] || null)
  const practiceDone = computed(
    () => practice.value.length > 0 && practiceIndex.value >= practice.value.length,
  )
  const correctCount = computed(
    () => practiceHistory.value.filter((h) => h.correct).length,
  )
  const mistakeCount = computed(
    () => practiceHistory.value.filter((h) => !h.correct).length,
  )

  function resetFromLesson() {
    exampleGroups.value = buildSeedExamples(lesson.value)
    practice.value = buildPracticeQuestions(lesson.value, { minCount: 15 })
    practiceIndex.value = 0
    practiceAnswer.value = ''
    practiceSelected.value = null
    practiceBuild.value = []
    practiceRemaining.value = []
    practiceFeedback.value = null
    practiceHistory.value = []
    remedialsLeft.value = 0
    summaryReady.value = false
    syncBuildTokens()
    chat.value = []
    conversationId.value = ''
    arabicExplanation.value = ''
  }

  async function loadArabicExplanation() {
    const L = lesson.value
    if (!L?.lesson_id && !L?.grammar_target) return
    arabicLoading.value = true
    arabicError.value = ''
    try {
      const res = await postTutorTurn({
        message:
          `Explain this English grammar naturally in Arabic for Arabic speakers (not a word-for-word translation). ` +
          `Topic: ${L.grammar_target}. Goal: ${L.lesson_goal}. ` +
          `Include short examples inside the Arabic explanation. Opening: ${L.teacher_opening}`,
        promptKind: 'explain',
        grammarId: L.grammar_target || undefined,
        lessonId: L.lesson_id || undefined,
        activityId: L.activity_id || undefined,
        studentLanguage: 'ar',
        conversationId: conversationId.value || undefined,
      })
      if (res.conversation_id) conversationId.value = res.conversation_id
      arabicExplanation.value = res.utterance || ''
    } catch (err) {
      arabicError.value = getErrorMessage(err)
    } finally {
      arabicLoading.value = false
    }
  }

  async function generateMoreExamples(category = 'daily') {
    const L = lesson.value
    examplesLoading.value = true
    examplesError.value = ''
    try {
      const res = await postTutorTurn({
        message:
          `Give 6 short English example sentences for grammar "${L.grammar_target}" ` +
          `in the category "${category}". One sentence per line. No numbering. ` +
          `Stay only on this grammar.`,
        promptKind: 'explain',
        grammarId: L.grammar_target || undefined,
        lessonId: L.lesson_id || undefined,
        studentLanguage: 'en',
        conversationId: conversationId.value || undefined,
      })
      if (res.conversation_id) conversationId.value = res.conversation_id
      const parsed = parseExamplesFromTutorText(res.utterance, category)
      const bucket = exampleGroups.value[category] ? category : 'daily'
      exampleGroups.value = {
        ...exampleGroups.value,
        [bucket]: [...(exampleGroups.value[bucket] || []), ...parsed],
      }
    } catch (err) {
      examplesError.value = getErrorMessage(err)
    } finally {
      examplesLoading.value = false
    }
  }

  async function sendChat() {
    const text = String(chatDraft.value || '').trim()
    if (!text || chatLoading.value) return
    const L = lesson.value

    chat.value = [...chat.value, { role: 'student', text }]
    chatDraft.value = ''
    chatError.value = ''

    if (isLikelyOffTopic(text, L)) {
      chat.value = [
        ...chat.value,
        {
          role: 'assistant',
          text:
            'I can only help with today’s grammar lesson — rules, examples, mistakes, and practice. ' +
            `Ask me something about “${L.grammar_target || 'this grammar'}”.`,
        },
      ]
      return
    }

    chatLoading.value = true
    try {
      const res = await postTutorTurn({
        message:
          `Lesson-scoped help only. Grammar: ${L.grammar_target}. ` +
          `Goal: ${L.lesson_goal}. Patterns: ${(L.expected_patterns || []).join('; ')}. ` +
          `Student question: ${text}`,
        promptKind: 'answer_question',
        grammarId: L.grammar_target || undefined,
        lessonId: L.lesson_id || undefined,
        activityId: L.activity_id || undefined,
        studentLanguage: /[\u0600-\u06FF]/.test(text) ? 'ar' : 'en',
        conversationId: conversationId.value || undefined,
      })
      if (res.conversation_id) conversationId.value = res.conversation_id
      chat.value = [
        ...chat.value,
        { role: 'assistant', text: res.utterance || 'Let’s look at that together.' },
      ]
    } catch (err) {
      chatError.value = getErrorMessage(err)
    } finally {
      chatLoading.value = false
    }
  }

  function playAudio(text, lang = 'en-US') {
    return speak(text, lang)
  }

  function normalize(s) {
    return String(s || '')
      .trim()
      .toLowerCase()
      .replace(/[^\w\s']/g, '')
      .replace(/\s+/g, ' ')
  }

  function checkAnswer() {
    const q = currentQuestion.value
    if (!q || practiceFeedback.value) return

    let given = ''
    if (q.type === 'mcq') given = practiceSelected.value
    else if (q.type === 'build') given = practiceBuild.value.join(' ')
    else given = practiceAnswer.value

    let correct = false
    if (q.type === 'mcq' || q.type === 'build' || q.type === 'correction' || q.type === 'fill') {
      correct = normalize(given) === normalize(q.answer)
    } else if (q.type === 'translation') {
      const n = normalize(given)
      correct =
        n.length > 2 &&
        (n.includes(normalize(q.acceptContains || q.answer).slice(0, 8)) ||
          normalize(q.answer)
            .split(' ')
            .slice(0, 2)
            .every((w) => n.includes(w)))
    }

    const entry = {
      id: q.id,
      correct,
      given,
      answer: q.answer,
      explanation: q.explanation,
      mistakeWhy: q.mistakeWhy || (correct ? '' : 'Review the pattern and try a similar item.'),
      type: q.type,
    }
    practiceHistory.value = [...practiceHistory.value, entry]
    practiceFeedback.value = entry

    if (!correct) {
      // Insert a similar remedial question next
      const remedial = {
        ...q,
        id: `${q.id}-remedial-${Date.now()}`,
        prompt: `Try a similar one:\n${q.prompt}`,
        difficulty: 'easy',
      }
      const next = practiceIndex.value + 1
      practice.value = [
        ...practice.value.slice(0, next),
        remedial,
        ...practice.value.slice(next),
      ]
      remedialsLeft.value += 1
    }
  }

  function continuePractice() {
    if (!practiceFeedback.value) return
    practiceFeedback.value = null
    practiceAnswer.value = ''
    practiceSelected.value = null
    practiceIndex.value += 1
    syncBuildTokens()
    if (practiceIndex.value >= practice.value.length) {
      summaryReady.value = true
    }
  }

  function syncBuildTokens() {
    const q = currentQuestion.value
    practiceBuild.value = []
    practiceRemaining.value = q?.type === 'build' ? [...(q.tokens || [])] : []
  }

  function toggleBuildToken(token, index) {
    practiceBuild.value = [...practiceBuild.value, token]
    practiceRemaining.value = practiceRemaining.value.filter((_, i) => i !== index)
  }

  function resetBuild() {
    syncBuildTokens()
  }

  function bootstrap() {
    resetFromLesson()
    loadArabicExplanation()
  }

  watch(
    () => lessonRef.value?.lesson_id,
    (id, prev) => {
      if (id && id !== prev) bootstrap()
    },
  )

  return {
    lesson,
    topic,
    difficulty,
    minutes,
    englishBlocks,
    arabicExplanation,
    arabicLoading,
    arabicError,
    exampleGroups,
    examplesLoading,
    examplesError,
    chat,
    chatDraft,
    chatLoading,
    chatError,
    practice,
    practiceIndex,
    practiceAnswer,
    practiceSelected,
    practiceBuild,
    practiceRemaining,
    practiceFeedback,
    practiceHistory,
    currentQuestion,
    practiceDone,
    correctCount,
    mistakeCount,
    summaryReady,
    bootstrap,
    loadArabicExplanation,
    generateMoreExamples,
    sendChat,
    playAudio,
    checkAnswer,
    continuePractice,
    toggleBuildToken,
    resetBuild,
  }
}
