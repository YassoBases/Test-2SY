import { api } from './client.js'

export async function fetchTeacherProfileCv() {
  const { data } = await api.get('/teacher/setup/cv')
  return data
}

export async function createTeacherQualification(payload) {
  const { data } = await api.post('/teacher/setup/qualifications', payload)
  return data
}

export async function updateTeacherQualification(id, payload) {
  const { data } = await api.put(`/teacher/setup/qualifications/${id}`, payload)
  return data
}

export async function deleteTeacherQualification(id) {
  await api.delete(`/teacher/setup/qualifications/${id}`)
}

export async function createTeacherTeachingExperience(payload) {
  const { data } = await api.post('/teacher/setup/teaching-experiences', payload)
  return data
}

export async function updateTeacherTeachingExperience(id, payload) {
  const { data } = await api.put(`/teacher/setup/teaching-experiences/${id}`, payload)
  return data
}

export async function deleteTeacherTeachingExperience(id) {
  await api.delete(`/teacher/setup/teaching-experiences/${id}`)
}

export async function createTeacherAchievement(payload) {
  const { data } = await api.post('/teacher/setup/achievements', payload)
  return data
}

export async function updateTeacherAchievement(id, payload) {
  const { data } = await api.put(`/teacher/setup/achievements/${id}`, payload)
  return data
}

export async function deleteTeacherAchievement(id) {
  await api.delete(`/teacher/setup/achievements/${id}`)
}
