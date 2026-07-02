import { api } from './client.js'
import { normalizeStudentCourseCard } from './normalizeCourse.js'

export async function fetchSubscriptionsCatalog() {
  const { data } = await api.get('/student/subscriptions')
  return {
    ...data,
    courses: (data.courses || []).map(normalizeStudentCourseCard),
  }
}

export async function subscribeToCourse(courseId, method = 'card') {
  const { data } = await api.post('/student/subscriptions/subscribe', {
    course_id: courseId,
    method,
  })
  return data
}
