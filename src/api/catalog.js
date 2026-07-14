import { api } from './client.js'

export async function fetchGrades() {
  const { data } = await api.get('/catalog/grades')
  return data
}

export async function fetchSubjects(grade) {
  const { data } = await api.get('/catalog/subjects', { params: { grade } })
  return data
}

export async function fetchTeachers(subjectId, grade) {
  const { data } = await api.get('/catalog/teachers', {
    params: { subject_id: subjectId, grade },
  })
  return data
}
