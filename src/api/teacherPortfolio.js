import { api } from './client.js'

export async function fetchTeacherPortfolio() {
  const { data } = await api.get('/teacher/setup/portfolio')
  return data
}

export async function updateTeachingImpact(payload) {
  const { data } = await api.put('/teacher/setup/portfolio/impact', payload)
  return data
}

export async function updateTeachingPhilosophy(payload) {
  const { data } = await api.put('/teacher/setup/portfolio/philosophy', payload)
  return data
}

export async function createWhyStudyPoint(payload) {
  const { data } = await api.post('/teacher/setup/why-study-points', payload)
  return data
}

export async function updateWhyStudyPoint(id, payload) {
  const { data } = await api.put(`/teacher/setup/why-study-points/${id}`, payload)
  return data
}

export async function deleteWhyStudyPoint(id) {
  await api.delete(`/teacher/setup/why-study-points/${id}`)
}

export async function uploadProfessionalDocument({ title, documentType, file, sortOrder = 0 }) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/teacher/setup/documents', form, {
    params: { title, document_type: documentType, sort_order: sortOrder },
  })
  return data
}

export async function updateProfessionalDocument(id, payload) {
  const { data } = await api.put(`/teacher/setup/documents/${id}`, payload)
  return data
}

export async function deleteProfessionalDocument(id) {
  await api.delete(`/teacher/setup/documents/${id}`)
}
