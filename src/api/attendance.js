import { api } from './client.js'

export async function fetchAttendanceSummaryApi() {
  const { data } = await api.get('/attendance/summary')
  return data
}

export async function fetchAttendanceRecordsApi(params = {}) {
  const { data } = await api.get('/attendance/records', { params })
  return data
}

export async function fetchAttendanceWeeklyApi() {
  const { data } = await api.get('/attendance/weekly')
  return data
}

export async function fetchAttendanceMonthlyApi() {
  const { data } = await api.get('/attendance/monthly')
  return data
}
