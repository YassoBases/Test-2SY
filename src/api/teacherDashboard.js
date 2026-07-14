import { api } from './client.js'

export async function fetchTeacherOverview() {
  const { data } = await api.get('/teacher/dashboard/overview')
  return data
}

export async function fetchTeacherGrades() {
  const { data } = await api.get('/teacher/dashboard/grades')
  return data
}

export async function fetchTeacherCourseDetail(courseId) {
  const { data } = await api.get(`/teacher/dashboard/courses/${courseId}`)
  return data
}

