import { api } from './client.js'

export async function fetchParentNoteCategories() {
  const { data } = await api.get('/parent/notes/categories')
  return data
}

export async function fetchParentNotes(params = {}) {
  const { data } = await api.get('/parent/notes', { params })
  return data
}

export async function fetchParentNote(noteId) {
  const { data } = await api.get(`/parent/notes/${noteId}`)
  return data
}

export async function fetchParentNotesUnreadCount(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/notes/unread-count', { params })
  return data
}

export async function acknowledgeParentNote(noteId) {
  const { data } = await api.post(`/parent/notes/${noteId}/acknowledge`)
  return data
}

export async function markParentNoteRead(noteId) {
  const { data } = await api.post(`/parent/notes/${noteId}/read`)
  return data
}

export async function replyParentNote(noteId, body) {
  const { data } = await api.post(`/parent/notes/${noteId}/reply`, { body })
  return data
}

export async function updateParentNoteReply(noteId, replyId, body) {
  const { data } = await api.patch(`/parent/notes/${noteId}/replies/${replyId}`, { body })
  return data
}

export async function deleteParentNoteReply(noteId, replyId) {
  const { data } = await api.delete(`/parent/notes/${noteId}/replies/${replyId}`)
  return data
}

export async function fetchTeacherParentNotes(studentId, limit = 20) {
  const { data } = await api.get(`/teacher/students/${studentId}/parent-notes`, {
    params: { limit },
  })
  return data
}

export async function fetchTeacherParentNote(studentId, noteId) {
  const { data } = await api.get(`/teacher/students/${studentId}/parent-notes/${noteId}`)
  return data
}

export async function fetchTeacherParentNoteCategories() {
  const { data } = await api.get('/teacher/students/parent-notes/categories')
  return data
}

export async function fetchTeacherParentNotePriorities() {
  const { data } = await api.get('/teacher/students/parent-notes/priorities')
  return data
}

export async function createTeacherParentNote(studentId, payload) {
  const { data } = await api.post(`/teacher/students/${studentId}/parent-notes`, payload)
  return data
}

export async function updateTeacherParentNote(studentId, noteId, payload) {
  const { data } = await api.patch(`/teacher/students/${studentId}/parent-notes/${noteId}`, payload)
  return data
}

export async function deleteTeacherParentNote(studentId, noteId) {
  await api.delete(`/teacher/students/${studentId}/parent-notes/${noteId}`)
}

export async function closeTeacherParentNote(studentId, noteId) {
  const { data } = await api.post(`/teacher/students/${studentId}/parent-notes/${noteId}/close`)
  return data
}

export async function replyTeacherParentNote(studentId, noteId, body) {
  const { data } = await api.post(`/teacher/students/${studentId}/parent-notes/${noteId}/reply`, { body })
  return data
}

export async function updateTeacherParentNoteReply(studentId, noteId, replyId, body) {
  const { data } = await api.patch(
    `/teacher/students/${studentId}/parent-notes/${noteId}/replies/${replyId}`,
    { body },
  )
  return data
}

export async function deleteTeacherParentNoteReply(studentId, noteId, replyId) {
  const { data } = await api.delete(
    `/teacher/students/${studentId}/parent-notes/${noteId}/replies/${replyId}`,
  )
  return data
}
