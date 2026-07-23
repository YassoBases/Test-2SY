import { api } from './client.js'

export function fetchSpeakingPromotionStatus() {
  return api.get('/student/languages/speaking/promotion-assessment/status').then((r) => r.data)
}

/** Creates a frozen SPA blueprint + distinct assessment identity (not started). */
export function createSpeakingPromotionAssessment() {
  return api.post('/student/languages/speaking/promotion-assessment').then((r) => r.data)
}

export function fetchSpeakingPromotionAssessment(assessmentId) {
  return api
    .get(`/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}`)
    .then((r) => r.data)
}

export function startSpeakingPromotionAssessment(assessmentId) {
  return api
    .post(`/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/start`)
    .then((r) => r.data)
}

export function retrySpeakingPromotionAssessment(assessmentId) {
  return api
    .post(`/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/retry`)
    .then((r) => r.data)
}

export function submitSpeakingPromotionAssessmentTask(assessmentId, body) {
  return api
    .post(
      `/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/submit`,
      body,
    )
    .then((r) => r.data)
}

export function completeSpeakingPromotionAssessment(assessmentId) {
  return api
    .post(
      `/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/complete`,
    )
    .then((r) => r.data)
}

export function abandonSpeakingPromotionAssessment(assessmentId) {
  return api
    .post(
      `/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/abandon`,
    )
    .then((r) => r.data)
}

export function fetchSpeakingPromotionAssessmentResult(assessmentId) {
  return api
    .get(
      `/student/languages/speaking/promotion-assessment/${encodeURIComponent(assessmentId)}/result`,
    )
    .then((r) => r.data)
}

/** S20 — apply official speaking CEFR after SPA PASS. */
export function promoteSpeakingOfficialCefr({ assessmentId = null, attemptId = null } = {}) {
  const body = {}
  if (assessmentId) body.assessment_id = assessmentId
  if (attemptId) body.attempt_id = attemptId
  return api.post('/student/languages/speaking/promote', body).then((r) => r.data)
}
