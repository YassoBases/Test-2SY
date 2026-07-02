import { api } from './client.js'

export async function searchTeacherStudents(params = {}) {
  const { data } = await api.get('/teacher/students', { params })
  return data
}

export async function fetchTeacherStudentProfile(studentId) {
  const { data } = await api.get(`/teacher/students/${studentId}`)
  return data
}

export async function createTeacherStudentNote(studentId, noteText) {
  const { data } = await api.post(`/teacher/students/${studentId}/notes`, { note_text: noteText })
  return data
}

export async function updateTeacherStudentNote(studentId, noteId, noteText) {
  const { data } = await api.patch(`/teacher/students/${studentId}/notes/${noteId}`, {
    note_text: noteText,
  })
  return data
}

export async function deleteTeacherStudentNote(studentId, noteId) {
  await api.delete(`/teacher/students/${studentId}/notes/${noteId}`)
}
