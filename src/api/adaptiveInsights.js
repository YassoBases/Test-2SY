import { api } from './client.js'

/** Thin wrapper for Adaptive insights (streak, confidence, advisory). */
export async function fetchAdaptiveInsights() {
  const { data } = await api.get('/student/adaptive/insights')
  return data
}
