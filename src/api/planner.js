import { api } from './client.js'

export async function fetchPlannerStateApi() {
  const { data } = await api.get('/student/planner')
  return data
}

export async function fetchPlannerSummaryApi() {
  const { data } = await api.get('/student/planner/summary')
  return data
}

export async function generatePlannerPlanApi() {
  const { data } = await api.post('/student/planner/generate')
  return data
}

export async function sendPlannerChatApi(message) {
  const { data } = await api.post('/student/planner/chat', { message })
  return data
}

export async function reoptimizePlannerApi() {
  const { data } = await api.post('/student/planner/optimize')
  return data
}

export async function completePlannerSessionApi(slotId) {
  const { data } = await api.post('/student/planner/sessions/complete', { slot_id: slotId })
  return data
}

export async function fetchTeacherStudentPlannerApi(studentId) {
  const { data } = await api.get(`/teacher/students/${studentId}/planner`)
  return data
}
