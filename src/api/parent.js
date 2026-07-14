import { api, getApiBaseUrl } from './client.js'
import { getSession } from '../utils/session.js'

export async function fetchParentDashboardApi(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/dashboard', { params })
  return data
}

export async function fetchParentLessonDetail(lessonId, studentId) {
  const { data } = await api.get(`/parent/lesson-progress/${lessonId}`, {
    params: studentId != null ? { student_id: studentId } : {},
  })
  return data
}

export async function fetchLinkedStudents() {
  const { data } = await api.get('/parent/students')
  return data
}

export async function linkParentStudent(linkCode) {
  const { data } = await api.post('/parent/link', { link_code: linkCode })
  return data
}

export async function fetchStudentLinkCode() {
  const { data } = await api.get('/parent/link-code')
  return data.link_code
}

export async function fetchParentExecutiveSummary(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/executive-summary', { params })
  return data
}

export async function fetchParentAcademicIntelligenceApi(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/academic-intelligence', { params })
  return data
}

export async function fetchParentRoutineApi(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/student-routine', { params })
  return data
}

export async function unlinkParentStudent(studentId) {
  await api.delete(`/parent/link/${studentId}`)
}

export async function fetchParentNotifications(studentId, limit = 50) {
  const params = { limit }
  if (studentId != null) params.student_id = studentId
  const { data } = await api.get('/parent/notifications', { params })
  return data
}

export async function markParentNotificationRead(notificationId, studentId) {
  const params = studentId != null ? { student_id: studentId } : {}
  const { data } = await api.post(`/parent/notifications/${notificationId}/read`, null, { params })
  return data
}

export async function fetchParentNotificationSettings(studentId) {
  const params = studentId != null ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/notification-settings', { params })
  return data
}

export async function updateParentNotificationSettings(studentId, payload) {
  const params = studentId != null ? { student_id: studentId } : {}
  const { data } = await api.put('/parent/notification-settings', payload, { params })
  return data
}

export async function fetchParentHistoricalReport(studentId, { period = 'this_week', startDate, endDate } = {}) {
  const params = { period }
  if (studentId != null) params.student_id = studentId
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  const { data } = await api.get('/parent/historical-report', { params })
  return data
}

function exportQueryParams(studentId, format, { period, startDate, endDate }) {
  const params = new URLSearchParams({ format, period })
  if (studentId != null) params.set('student_id', String(studentId))
  if (startDate) params.set('start_date', startDate)
  if (endDate) params.set('end_date', endDate)
  return params
}

const MIME = {
  csv: 'text/csv',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  pdf: 'application/pdf',
}

/**
 * Large PDF exports (~10MB+) can fail through axios+blob with net::ERR_FAILED 200.
 * Use fetch + arrayBuffer for binary exports.
 */
export async function exportParentHistoricalReport(studentId, format, { period = 'this_week', startDate, endDate } = {}) {
  const params = exportQueryParams(studentId, format, { period, startDate, endDate })
  const url = `${getApiBaseUrl()}/parent/historical-report/export?${params}`
  const token = getSession()?.accessToken
  const headers = { Accept: '*/*' }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(url, { headers, credentials: 'same-origin' })
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const json = await res.json()
      detail = json.detail || detail
    } catch {
      /* binary error body */
    }
    const err = new Error(detail)
    err.response = { status: res.status, data: { detail } }
    throw err
  }

  const buffer = await res.arrayBuffer()
  const type = res.headers.get('content-type') || MIME[format] || 'application/octet-stream'
  return new Blob([buffer], { type })
}

export async function fetchParentSubjectsTeachers(studentId) {
  const params = studentId != null ? { student_id: studentId } : {}
  const { data } = await api.get('/parent/subjects-teachers', { params })
  return data
}

export async function fetchParentCourseTeacherProfile(courseId, studentId) {
  const params = studentId != null ? { student_id: studentId } : {}
  const { data } = await api.get(`/parent/courses/${courseId}/teacher-profile`, { params })
  return data
}
