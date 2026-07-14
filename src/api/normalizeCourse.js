import { teacherImageFromEntity } from '../utils/teacherAvatar.js'

/** Unify teacher avatar fields from student course API payloads. */
export function normalizeStudentCourseCard(course) {
  if (!course || typeof course !== 'object') return course
  const url = teacherImageFromEntity(course)
  return {
    ...course,
    teacher_image_url: url,
    teacherImageUrl: url,
    avatar_url: url,
  }
}

export function normalizeStudentDashboard(data) {
  if (!data || typeof data !== 'object') return data
  return {
    ...data,
    courses: (data.courses || []).map(normalizeStudentCourseCard),
  }
}
