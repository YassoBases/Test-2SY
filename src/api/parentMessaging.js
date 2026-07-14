import { api } from './client.js'

export async function fetchParentTeachers() {
  const { data } = await api.get('/parent/messaging/teachers')
  return data
}

export async function fetchParentMessagingSummary() {
  const { data } = await api.get('/parent/messaging/summary')
  return data
}

export async function openParentTeacherChat(teacherId, { studentId, courseId }) {
  const { data } = await api.post(`/parent/messaging/teachers/${teacherId}/open-chat`, {
    student_id: studentId,
    course_id: courseId,
  })
  return data
}
