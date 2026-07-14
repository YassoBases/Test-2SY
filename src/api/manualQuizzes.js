import { api } from './client.js'

// Teacher
export async function fetchTeacherManualQuizzes(courseId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/manual-quizzes`)
  return data
}

export async function createManualQuiz(courseId, payload) {
  const { data } = await api.post(`/teacher/courses/${courseId}/manual-quizzes`, payload)
  return data
}

export async function fetchManualQuizDetail(courseId, quizId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/manual-quizzes/${quizId}`)
  return data
}

export async function updateManualQuiz(courseId, quizId, payload) {
  const { data } = await api.put(`/teacher/courses/${courseId}/manual-quizzes/${quizId}`, payload)
  return data
}

export async function deleteManualQuiz(courseId, quizId) {
  await api.delete(`/teacher/courses/${courseId}/manual-quizzes/${quizId}`)
}

export async function addManualQuestion(courseId, quizId, payload) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/questions`,
    payload,
  )
  return data
}

export async function updateManualQuestion(courseId, quizId, questionId, payload) {
  const { data } = await api.put(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/questions/${questionId}`,
    payload,
  )
  return data
}

export async function deleteManualQuestion(courseId, quizId, questionId) {
  await api.delete(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/questions/${questionId}`,
  )
}

export async function fetchManualQuizResults(courseId, quizId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/manual-quizzes/${quizId}/results`)
  return data
}

export async function fetchManualQuizAttempt(courseId, quizId, attemptId) {
  const { data } = await api.get(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/attempts/${attemptId}`,
  )
  return data
}

export async function gradeManualEssay(courseId, quizId, attemptId, questionId, payload) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/attempts/${attemptId}/questions/${questionId}/grade`,
    payload,
  )
  return data
}

export async function fetchManualQuizAnalytics(courseId, quizId) {
  const { data } = await api.get(
    `/teacher/courses/${courseId}/manual-quizzes/${quizId}/analytics`,
  )
  return data
}

export async function fetchCourseManualQuizAnalytics(courseId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/manual-quiz-analytics`)
  return data
}

// Student
export async function fetchStudentManualQuizzes(courseId) {
  const { data } = await api.get(`/student/courses/${courseId}/manual-quizzes`)
  return data
}

export async function fetchManualQuizTake(quizId) {
  const { data } = await api.get(`/student/manual-quizzes/${quizId}`)
  return data
}

export async function startManualQuiz(quizId) {
  const { data } = await api.post(`/student/manual-quizzes/${quizId}/start`)
  return data
}

export async function saveManualQuizAnswers(attemptId, answers) {
  await api.patch(`/student/manual-quiz-attempts/${attemptId}/answers`, { answers })
}

export async function submitManualQuiz(attemptId) {
  const { data } = await api.post(`/student/manual-quiz-attempts/${attemptId}/submit`)
  return data
}

export async function fetchManualQuizAttemptResult(attemptId) {
  const { data } = await api.get(`/student/manual-quiz-attempts/${attemptId}`)
  return data
}

export const QUESTION_TYPES = [
  { value: 'multiple_choice', label: 'اختيار من متعدد' },
  { value: 'true_false', label: 'صح / خطأ' },
  { value: 'short_answer', label: 'إجابة قصيرة' },
  { value: 'essay', label: 'مقالي (تصحيح يدوي)' },
]
