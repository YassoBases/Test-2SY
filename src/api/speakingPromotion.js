import { api } from './client.js'

export function fetchSpeakingPromotionStatus() {
  return api.get('/student/languages/speaking/promotion-assessment/status').then((r) => r.data)
}

/** Preview-only: creates/returns frozen SPA blueprint. Does not run or score the assessment. */
export function createSpeakingPromotionAssessment() {
  return api.post('/student/languages/speaking/promotion-assessment').then((r) => r.data)
}

export function fetchSpeakingPromotionAssessment(assessmentId) {
  return api
    .get(`/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}`)
    .then((r) => r.data)
}
