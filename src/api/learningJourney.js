import { api } from './client.js'

/** Read-only CEFR stage graph for English Journey UI. */
export async function fetchLearningJourney() {
  const { data } = await api.get('/student/languages/journey')
  return data
}
