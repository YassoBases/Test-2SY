import { api } from './client.js'

const VOICE_CHAT_TIMEOUT_MS = 5 * 60 * 1000

export async function fetchStudentLessons() {
  const { data } = await api.get('/student/lessons')
  return data
}

export async function fetchStudentLesson(id) {
  const { data } = await api.get(`/student/lesson/${id}`)
  return data
}

export async function sendChatApi({ lessonId, message }) {
  const { data } = await api.post('/student/chat', {
    lesson_id: lessonId,
    message,
  })
  return data
}

export async function sendVoiceChatApi({ lessonId, file }) {
  const form = new FormData()
  form.append('lesson_id', String(lessonId))
  form.append('file', file)

  const { data } = await api.post('/student/chat/voice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: VOICE_CHAT_TIMEOUT_MS,
  })
  return data
}

export async function clearStudentChatApi(lessonId) {
  await api.delete(`/student/lesson/${lessonId}/chat`)
}

export async function fetchQuizApi(lessonId) {
  const { data } = await api.get(`/student/quiz/${lessonId}`)
  return data
}

export async function regenerateQuizApi(lessonId) {
  const { data } = await api.post(`/student/lesson/${lessonId}/quiz/regenerate`)
  return data.quizQuestions || []
}

export async function generateRemedialQuestionsApi({ lessonId, answers }) {
  const { data } = await api.post(`/student/lesson/${lessonId}/quiz/remedial`, {
    answers,
  })
  return data.questions || []
}

export async function submitQuizApi({ lessonId, answers }) {
  const { data } = await api.post('/student/quiz/submit', {
    lesson_id: lessonId,
    answers,
  })
  return data
}

export async function fetchLinkedParents() {
  const { data } = await api.get('/student/linked-parents')
  return data
}

export async function getProfileApi() {
  const { data } = await api.get('/student/profile')
  return data
}

export async function updateProfileApi(payload) {
  const { data } = await api.put('/student/profile', payload)
  return data
}
