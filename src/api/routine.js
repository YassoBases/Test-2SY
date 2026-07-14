import { api } from './client.js'

export const saveOnboarding = (data) => api.post('/student/routine/onboarding', data).then(r => r.data)
export const getRoutineProfile = () => api.get('/student/routine/profile').then(r => r.data)
export const updateSettings = (data) => api.patch('/student/routine/profile', data).then(r => r.data)
export const deleteProfile = () => api.delete('/student/routine/profile').then(r => r.data)
export const chatRoutine = (message) => api.post('/student/routine/chat', { message }).then(r => r.data)
export const confirmSummary = (days) => api.post('/student/routine/confirm-summary', { days }).then(r => r.data)
export const editDay = (day) => api.post('/student/routine/edit-day', { day }).then(r => r.data)
export const confirmSchedule = (days) => api.post('/student/routine/confirm', { days }).then(r => r.data)
export const getWeekRoutine = () => api.get('/student/routine/week').then(r => r.data)
export const regenerateSchedule = () => api.post('/student/routine/regenerate').then(r => r.data)
export const renewWeek = () => api.post('/student/routine/renew-week').then(r => r.data)
export const reviewRoutine = () => api.post('/student/routine/review').then(r => r.data)
export const uploadExamSchedule = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/student/routine/upload-exam', fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}
export const saveConfirmedExams = (exams) => api.post('/student/routine/save-exams', { exams }).then(r => r.data)
export const completeSlot = (id) => api.post(`/student/routine/slots/${id}/complete`).then(r => r.data)
export const missSlot = (id) => api.post(`/student/routine/slots/${id}/miss`).then(r => r.data)
export const undoSlot = (id) => api.post(`/student/routine/slots/${id}/undo`).then(r => r.data)
