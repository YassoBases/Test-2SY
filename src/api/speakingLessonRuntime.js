import { api } from './client.js'

export function openSpeakingLessonRuntime({ packageId, forceRestart } = {}) {
  return api
    .post('/student/languages/speaking/lesson-runtime/open', {
      package_id: packageId || null,
      force_restart: Boolean(forceRestart),
    })
    .then((r) => r.data)
}

export function fetchActiveSpeakingLessonRuntime() {
  return api.get('/student/languages/speaking/lesson-runtime/active').then((r) => r.data)
}

export function advanceSpeakingLessonRuntime() {
  return api.post('/student/languages/speaking/lesson-runtime/advance').then((r) => r.data)
}

export function markSpeakingLessonVocabViewed(vocabularyId) {
  return api
    .post('/student/languages/speaking/lesson-runtime/vocabulary/viewed', {
      vocabulary_id: vocabularyId,
    })
    .then((r) => r.data)
}

export function markSpeakingLessonBlockViewed(blockId) {
  return api
    .post('/student/languages/speaking/lesson-runtime/teaching-blocks/viewed', {
      block_id: blockId,
    })
    .then((r) => r.data)
}

export function markSpeakingLessonMiniPrepComplete() {
  return api
    .post('/student/languages/speaking/lesson-runtime/mini-practice/prep-complete')
    .then((r) => r.data)
}
