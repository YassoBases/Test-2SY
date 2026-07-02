import { api } from './client.js'

export async function fetchGamificationProfileApi() {
  const { data } = await api.get('/student/gamification')
  return data
}
