import { api } from './client.js'

const LESSON_PROCESS_TIMEOUT_MS = 10 * 60 * 1000

export async function fetchTeacherContent() {
  const { data } = await api.get('/teacher/content')
  return data
}

export async function uploadPdfApi({ file, subject, grade, title, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  form.append('subject', subject)
  form.append('grade', grade)
  if (title) form.append('title', title)
  if (lessonId) form.append('lesson_id', String(lessonId))

  const { data } = await api.post('/teacher/upload/pdf', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) return Math.round((e.loaded * 100) / e.total)
      return 0
    },
  })
  return data
}

export async function uploadVoiceApi({ file, lessonId }) {
  const form = new FormData()
  form.append('file', file)
  if (lessonId) form.append('lesson_id', String(lessonId))
  const { data } = await api.post('/teacher/upload/voice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function fetchTeacherVoiceSample() {
  const { data } = await api.get('/teacher/voice-sample')
  return data
}

export async function fetchTeacherVoiceProfile() {
  const { data } = await api.get('/teacher/voice-profile')
  return data
}

export async function uploadTeacherVoiceSample(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/teacher/voice-sample', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function regenerateTeacherVoiceSample(sampleId) {
  const { data } = await api.post(`/teacher/voice-samples/${sampleId}/regenerate`)
  return data
}

export async function previewTeacherVoiceSample(sampleId, text) {
  const { data } = await api.post(`/teacher/voice-samples/${sampleId}/preview`, { text })
  return data
}

export async function deleteTeacherVoiceSample(sampleId) {
  const { data } = await api.delete(`/teacher/voice-samples/${sampleId}`)
  return data
}

export async function processLessonApi(lessonId) {
  const { data } = await api.post(`/teacher/lessons/${lessonId}/process`, null, {
    timeout: LESSON_PROCESS_TIMEOUT_MS,
  })
  return data
}

export async function deleteLessonApi(lessonId) {
  await api.delete(`/teacher/lessons/${lessonId}`)
}
