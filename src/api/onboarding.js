import { api } from './client.js'

export async function fetchOnboardingStatus() {
  const { data } = await api.get('/student/onboarding/status')
  return data
}

export async function saveOnboardingGrade(grade) {
  const { data } = await api.put('/student/onboarding/grade', { grade })
  return data
}

export async function saveOnboardingSubjects(subjectIds) {
  const { data } = await api.put('/student/onboarding/subjects', { subject_ids: subjectIds })
  return data
}

export async function saveOnboardingTeachers(choices) {
  const { data } = await api.put('/student/onboarding/teachers', { choices })
  return data
}

export async function completeOnboarding() {
  const { data } = await api.post('/student/onboarding/complete')
  return data
}
