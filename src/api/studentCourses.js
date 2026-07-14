import { api } from './client.js'
import { normalizeStudentCourseCard, normalizeStudentDashboard } from './normalizeCourse.js'

export async function fetchStudentDashboard() {
  const { data } = await api.get('/student/dashboard')
  return normalizeStudentDashboard(data)
}

export async function fetchStudentCourse(courseId) {
  const { data } = await api.get(`/student/courses/${courseId}`)
  return normalizeStudentCourseCard(data)
}

export async function fetchCourseTeacherProfile(courseId) {
  const { data } = await api.get(`/student/courses/${courseId}/teacher-profile`)
  return data
}

export async function openCourseTeacherChat(courseId, { includeParent = false } = {}) {
  const { data } = await api.post(`/student/courses/${courseId}/open-teacher-chat`, {
    include_parent: includeParent,
  })
  return data
}

export async function markLessonComplete(lessonId) {
  await api.post(`/student/lessons/${lessonId}/complete`)
}

export async function fetchLessonProgress(lessonId) {
  const { data } = await api.get(`/student/lessons/${lessonId}/progress`)
  return data
}

export async function updateLessonProgress(lessonId, payload) {
  const { data } = await api.post(`/student/lessons/${lessonId}/progress`, payload)
  return data
}

export async function verifyLessonCompletion(lessonId) {
  const { data } = await api.post(`/student/lessons/${lessonId}/verify-completion`)
  return data
}

export async function fetchCourseLessonProgress(courseId) {
  const { data } = await api.get(`/student/courses/${courseId}/lesson-progress`)
  return data
}

export async function fetchLessonAiStatus(lessonId) {
  const { data } = await api.get(`/student/lessons/${lessonId}/status`)
  return data
}
