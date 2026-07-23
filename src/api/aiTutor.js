import { api } from './client.js'

export async function fetchTutorStatus() {
  const { data } = await api.get('/student/tutor/status')
  return data
}

export async function fetchTutorContext(params = {}) {
  const { data } = await api.get('/student/tutor/context', {
    params: {
      grammar_id: params.grammarId || undefined,
      lesson_id: params.lessonId || undefined,
    },
  })
  return data
}

/**
 * Conversational tutor turn — explain / hint / answer_question / etc.
 * Does not write Grammar mastery or progression.
 */
export async function postTutorTurn(payload = {}) {
  const { data } = await api.post('/student/tutor/turn', {
    message: payload.message || '',
    prompt_kind: payload.promptKind || 'answer_question',
    conversation_id: payload.conversationId || null,
    grammar_id: payload.grammarId || null,
    lesson_id: payload.lessonId || null,
    activity_id: payload.activityId || null,
    step_id: payload.stepId || null,
    student_language: payload.studentLanguage || 'en',
    persona_id: payload.personaId || null,
  })
  return data
}
