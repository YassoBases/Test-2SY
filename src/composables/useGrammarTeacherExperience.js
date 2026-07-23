/**
 * P1 — Cloud AI Teacher orchestration (frontend only).
 * Sits beside P0 session runtime; does not modify the runtime module.
 * Uses existing Tutor APIs for Ask Anytime.
 */
import { computed, ref, watch } from 'vue'
import { getErrorMessage } from '../api/client.js'
import { fetchTutorContext, postTutorTurn } from '../api/aiTutor.js'
import { buildTeachingCards } from '../utils/grammarTeachingCards.js'

const MOODS = ['encouraging', 'curious', 'proud', 'calm']

export function useGrammarTeacherExperience({
  lesson,
  currentStage,
  teacherVoiceState,
  listeningState,
  speakingState,
  setTeacherContext,
  memory,
} = {}) {
  const tutorEnabled = ref(null)
  const teacherName = ref('Alex')
  const teacherFocus = ref('')
  const teacherMood = ref('encouraging')
  const teacherMessage = ref('')
  const thinking = ref(false)
  const askOpen = ref(false)
  const askDraft = ref('')
  const askError = ref('')
  const conversationId = ref('')
  const questionsAsked = ref([])
  const cardsCompleted = ref([])
  const examplesShown = ref([])
  const teachingCards = ref([])
  const teachCardIndex = ref(0)
  const lastUtterance = ref('')

  const presenceState = computed(() => {
    if (thinking.value) return 'thinking'
    if (teacherVoiceState?.value === 'listening' || listeningState?.value) return 'listening'
    if (teacherVoiceState?.value === 'teacher_speaking' || speakingState?.value) {
      return 'speaking'
    }
    return 'idle'
  })

  const currentTeachCard = computed(
    () => teachingCards.value[teachCardIndex.value] || null,
  )

  const teachCardsRemaining = computed(
    () => Math.max(0, teachingCards.value.length - teachCardIndex.value - 1),
  )

  const allTeachCardsSeen = computed(() => {
    if (!teachingCards.value.length) return true
    return teachCardIndex.value >= teachingCards.value.length - 1
  })

  function persistTeacherMemory() {
    if (typeof setTeacherContext !== 'function') return
    setTeacherContext({
      teacherName: teacherName.value,
      teacherMood: teacherMood.value,
      teacherFocus: teacherFocus.value,
      conversationId: conversationId.value,
      questionsAsked: questionsAsked.value,
      cardsCompleted: cardsCompleted.value,
      examplesShown: examplesShown.value,
      teachCardIndex: teachCardIndex.value,
      lastUtterance: lastUtterance.value,
    })
  }

  function hydrateFromMemory() {
    const ctx = memory?.value?.teacherContext || {}
    if (ctx.teacherName) teacherName.value = ctx.teacherName
    if (ctx.teacherMood) teacherMood.value = ctx.teacherMood
    if (ctx.conversationId) conversationId.value = ctx.conversationId
    if (Array.isArray(ctx.questionsAsked)) questionsAsked.value = ctx.questionsAsked
    if (Array.isArray(ctx.cardsCompleted)) cardsCompleted.value = ctx.cardsCompleted
    if (Array.isArray(ctx.examplesShown)) examplesShown.value = ctx.examplesShown
    if (typeof ctx.teachCardIndex === 'number') teachCardIndex.value = ctx.teachCardIndex
    if (ctx.lastUtterance) {
      lastUtterance.value = ctx.lastUtterance
      teacherMessage.value = ctx.lastUtterance
    }
  }

  function setPresence(kind) {
    if (!teacherVoiceState) return
    if (kind === 'thinking') {
      thinking.value = true
      teacherVoiceState.value = 'idle'
      return
    }
    thinking.value = false
    if (kind === 'speaking') teacherVoiceState.value = 'teacher_speaking'
    else if (kind === 'listening') {
      teacherVoiceState.value = 'listening'
      if (listeningState) listeningState.value = true
    } else {
      teacherVoiceState.value = 'idle'
      if (listeningState) listeningState.value = false
      if (speakingState) speakingState.value = false
    }
  }

  function speakLocal(message, { mood, focus } = {}) {
    teacherMessage.value = message
    lastUtterance.value = message
    if (mood) teacherMood.value = mood
    if (focus) teacherFocus.value = focus
    setPresence('speaking')
    persistTeacherMemory()
    // Visual-only speaking pulse; no audio in P1.
    window.setTimeout(() => {
      if (teacherMessage.value === message) setPresence('idle')
    }, 900)
  }

  function rebuildTeachingCards() {
    teachingCards.value = buildTeachingCards(lesson?.value || lesson)
    const max = Math.max(0, teachingCards.value.length - 1)
    if (teachCardIndex.value > max) teachCardIndex.value = 0
  }

  async function loadTutorContext() {
    const L = lesson?.value || lesson
    if (!L?.lesson_id && !L?.grammar_target) return
    try {
      const ctx = await fetchTutorContext({
        grammarId: L.grammar_target || undefined,
        lessonId: L.lesson_id || undefined,
      })
      tutorEnabled.value = !!ctx?.enabled
      const persona = ctx?.teacher_persona || {}
      if (persona.display_name || persona.name) {
        teacherName.value = persona.display_name || persona.name
      }
      if (ctx?.display_name && !teacherFocus.value) {
        teacherFocus.value = ctx.display_name
      }
      persistTeacherMemory()
    } catch {
      tutorEnabled.value = false
    }
  }

  function stageScript(stage) {
    const L = lesson?.value || lesson || {}
    const topic = L.grammar_target || L.lesson_title || 'today’s grammar'
    switch (stage) {
      case 'WELCOME':
        return {
          mood: 'encouraging',
          focus: topic,
          message:
            L.teacher_opening
              ? `Welcome! Today we’ll work on ${topic}. ${String(L.teacher_opening).slice(0, 160)}${String(L.teacher_opening).length > 160 ? '…' : ''}`
              : `Welcome! I’m glad you’re here. Today we’ll learn ${topic} together, step by step.`,
        }
      case 'MISSION':
        return {
          mood: 'curious',
          focus: 'Today’s mission',
          message: L.lesson_goal
            ? `Today we're going to learn… ${L.lesson_goal}`
            : `Today we're going to learn how to use ${topic} in real situations.`,
        }
      case 'LEARN':
        return {
          mood: 'calm',
          focus: 'Teaching',
          message:
            'I’ll explain this in small steps. Take one card at a time — ask me anytime.',
        }
      case 'PRACTICE':
        return {
          mood: 'encouraging',
          focus: 'Practice',
          message: 'Your turn to try. I’ll stay with you and explain every answer later.',
        }
      case 'SPEAKING':
        return {
          mood: 'curious',
          focus: 'Speaking',
          message: 'Speaking practice will live here soon. For now, keep going with me.',
        }
      case 'WRITING':
        return {
          mood: 'calm',
          focus: 'Writing',
          message: 'Writing coach will join this stage next. Continue when you’re ready.',
        }
      case 'REFLECTION':
        return {
          mood: 'proud',
          focus: 'Reflection',
          message: L.completion_message
            ? String(L.completion_message)
            : 'Nice work today. Let’s notice what clicked before we finish.',
        }
      case 'COMPLETE':
        return {
          mood: 'proud',
          focus: 'Complete',
          message: 'You made it through the session. Finish when you’re ready — I’m proud of you.',
        }
      default:
        return {
          mood: 'encouraging',
          focus: topic,
          message: 'I’m here with you.',
        }
    }
  }

  function narrateStage(stage) {
    const script = stageScript(stage)
    speakLocal(script.message, { mood: script.mood, focus: script.focus })
  }

  function advanceTeachCard() {
    if (allTeachCardsSeen.value) return false
    const current = currentTeachCard.value
    if (current?.id && !cardsCompleted.value.includes(current.id)) {
      cardsCompleted.value = [...cardsCompleted.value, current.id]
    }
    if (current?.kind === 'example' && current.example) {
      examplesShown.value = [...examplesShown.value, current.example]
    }
    teachCardIndex.value += 1
    const nextCard = currentTeachCard.value
    if (nextCard?.teacherLine) {
      speakLocal(nextCard.teacherLine, {
        mood: nextCard.mood || 'calm',
        focus: nextCard.title || 'Teaching',
      })
    } else {
      persistTeacherMemory()
    }
    return true
  }

  function openAsk() {
    askOpen.value = true
    askDraft.value = ''
    askError.value = ''
    setPresence('listening')
  }

  function closeAsk() {
    askOpen.value = false
    askDraft.value = ''
    askError.value = ''
    setPresence('idle')
  }

  async function askTeacher(message, promptKind = 'answer_question') {
    const text = String(message || askDraft.value || '').trim()
    if (!text) {
      askError.value = 'Ask a short question about today’s grammar.'
      return null
    }
    const L = lesson?.value || lesson || {}
    askError.value = ''
    thinking.value = true
    setPresence('thinking')
    try {
      const res = await postTutorTurn({
        message: text,
        promptKind,
        conversationId: conversationId.value || undefined,
        grammarId: L.grammar_target || undefined,
        lessonId: L.lesson_id || undefined,
        activityId: L.activity_id || undefined,
        stepId: currentTeachCard.value?.id || currentStage?.value || undefined,
        studentLanguage: 'en',
      })
      conversationId.value = res.conversation_id || conversationId.value
      questionsAsked.value = [
        ...questionsAsked.value,
        { q: text, a: res.utterance, at: Date.now() },
      ]
      speakLocal(res.utterance || 'Let’s look at that together.', {
        mood: 'encouraging',
        focus: 'Your question',
      })
      askDraft.value = ''
      askOpen.value = false
      persistTeacherMemory()
      return res
    } catch (err) {
      askError.value = getErrorMessage(err)
      setPresence('idle')
      return null
    } finally {
      thinking.value = false
    }
  }

  function celebrateCard() {
    const mood = MOODS[teachCardIndex.value % MOODS.length]
    teacherMood.value = mood
  }

  function bootstrap() {
    hydrateFromMemory()
    rebuildTeachingCards()
    loadTutorContext()
    if (currentStage?.value) narrateStage(currentStage.value)
  }

  if (currentStage) {
    watch(currentStage, (stage) => {
      if (stage === 'LEARN') {
        rebuildTeachingCards()
        const card = currentTeachCard.value
        if (card?.teacherLine) {
          speakLocal(card.teacherLine, {
            mood: card.mood || 'calm',
            focus: card.title || 'Teaching',
          })
          return
        }
      }
      narrateStage(stage)
    })
  }

  if (lesson && typeof lesson === 'object' && 'value' in lesson) {
    watch(
      () => lesson.value?.lesson_id,
      () => {
        rebuildTeachingCards()
        loadTutorContext()
      },
    )
  }

  return {
    tutorEnabled,
    teacherName,
    teacherFocus,
    teacherMood,
    teacherMessage,
    thinking,
    presenceState,
    askOpen,
    askDraft,
    askError,
    conversationId,
    questionsAsked,
    cardsCompleted,
    examplesShown,
    teachingCards,
    teachCardIndex,
    currentTeachCard,
    teachCardsRemaining,
    allTeachCardsSeen,
    lastUtterance,
    bootstrap,
    narrateStage,
    speakLocal,
    openAsk,
    closeAsk,
    askTeacher,
    advanceTeachCard,
    celebrateCard,
    rebuildTeachingCards,
    persistTeacherMemory,
    setPresence,
  }
}
