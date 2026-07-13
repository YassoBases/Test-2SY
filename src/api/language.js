import { api } from './client.js'

export async function fetchLanguageAccess() {
  const { data } = await api.get('/student/languages/access')
  return data
}

export async function fetchLanguageProduct() {
  const { data } = await api.get('/student/languages/product')
  return data
}

export async function subscribeLanguage(method = 'card') {
  const { data } = await api.post('/student/languages/subscribe', { method })
  return data
}

export async function fetchPlacementHistory() {
  const { data } = await api.get('/student/languages/placement-history')
  return data
}

export async function fetchLanguageHub() {
  const { data } = await api.get('/student/languages/hub')
  return data
}

export async function fetchReadingLessons() {
  const { data } = await api.get('/student/languages/reading')
  return data
}

export async function fetchReadingLesson(contentId) {
  const { data } = await api.get(`/student/languages/reading/${contentId}`)
  return data
}

export async function submitReadingLesson(contentId, answers, durationSeconds = null) {
  const { data } = await api.post(`/student/languages/reading/${contentId}/submit`, {
    answers,
    duration_seconds: durationSeconds,
  })
  return data
}

// Adaptive reading: the next passage at the student's level (generates content on demand).
// `length` (short|medium|long) controls how long a freshly generated passage is.
export async function fetchNextReading(length = '') {
  const { data } = await api.get('/student/languages/reading/next', { params: length ? { length } : {} })
  return data
}

// Pre-computed definitions for every hard word in a passage (so taps are instant).
export async function fetchReadingGlossary(contentId) {
  const { data } = await api.get(`/student/languages/reading/${contentId}/glossary`)
  return data
}

// Explain one sentence from a passage (meaning + a grammar note) for the learner's level.
export async function explainReadingSentence(sentence, level = 'A2') {
  const { data } = await api.post('/student/languages/reading/explain-sentence', { sentence, level })
  return data
}

// Narration audio for a passage (read-along), synthesized + cached server-side on first request.
export async function fetchReadingAudio(contentId) {
  const { data } = await api.get(`/student/languages/reading/${contentId}/audio`)
  return data
}

// Grade the student's own-words summary of a passage for comprehension.
export async function submitReadingSummary(contentId, summary) {
  const { data } = await api.post(`/student/languages/reading/${contentId}/summary`, { summary })
  return data
}

// Save a word the learner met (e.g. tapped while reading) to their vocabulary bank.
export async function saveVocabularyWord(word) {
  const { data } = await api.post('/student/languages/vocabulary/save', { word })
  return data
}

// Reading interests: curated options + the learner's picks (drives generated-passage topics).
export async function fetchReadingTopics() {
  const { data } = await api.get('/student/languages/reading/topics')
  return data
}
export async function saveReadingTopics(topics) {
  const { data } = await api.put('/student/languages/reading/topics', { topics })
  return data
}

// Reading library: passages the learner has completed (for re-reading).
export async function fetchReadingHistory() {
  const { data } = await api.get('/student/languages/reading/history')
  return data
}

// Reading analytics: WPM trend, comprehension, and per-skill strengths/gaps.
export async function fetchReadingInsights() {
  const { data } = await api.get('/student/languages/reading/insights')
  return data
}

// Adaptive listening: the next clip at the student's level (generates + voices on demand).
export async function fetchNextListening() {
  const { data } = await api.get('/student/languages/listening/next')
  return data
}

export async function fetchListeningLessons() {
  const { data } = await api.get('/student/languages/listening')
  return data
}

export async function fetchListeningLesson(contentId) {
  const { data } = await api.get(`/student/languages/listening/${contentId}`)
  return data
}

export async function submitListeningLesson(contentId, answers) {
  const { data } = await api.post(`/student/languages/listening/${contentId}/submit`, { answers })
  return data
}

export async function fetchLanguageProgress() {
  const { data } = await api.get('/student/languages/progress')
  return data
}

export async function fetchVocabulary() {
  const { data } = await api.get('/student/languages/vocabulary')
  return data
}

// Fetch one card's detail — lazily AI-enriches a stub word (definition/example) and caches it.
export async function fetchVocabularyCard(contentId) {
  const { data } = await api.get(`/student/languages/vocabulary/${contentId}`)
  return data
}

export async function reviewVocabularyCard(contentId, quality) {
  const { data } = await api.post(`/student/languages/vocabulary/${contentId}/review`, { quality })
  return data
}

// On-demand AI word lookup (English-only metadata: definition, example, pronunciation, synonyms).
export async function analyzeWord(word, level = 'A2') {
  const { data } = await api.post('/student/languages/vocabulary/analyze', { word, level })
  return data
}

// Daily fill-in-the-blanks review challenge built from the student's due words (English only).
export async function fetchVocabularyChallenge() {
  const { data } = await api.get('/student/languages/vocabulary/challenge')
  return data
}

// Report a finished daily challenge so it feeds the learner model. results: [{word, correct}].
export async function submitVocabularyChallenge(results) {
  const { data } = await api.post('/student/languages/vocabulary/challenge/submit', { results })
  return data
}

// Unified learner-model snapshot: component mastery + per-skill confidence + due-review count.
export async function fetchLearnerModelProfile() {
  const { data } = await api.get('/student/languages/learner-model/profile')
  return data
}

// Adaptive "smart review" MCQs targeting the learner's weakest knowledge components.
// `skill` (optional) drills one skill (reading/listening/writing/speaking).
export async function fetchLearnerPractice(count = 4, skill = '') {
  const { data } = await api.get('/student/languages/learner-model/practice', {
    params: skill ? { count, skill } : { count },
  })
  return data
}

// Report answered smart-review questions. results: [{component_code, correct}].
export async function submitLearnerPractice(results) {
  const { data } = await api.post('/student/languages/learner-model/practice/submit', { results })
  return data
}

// Global English dictionary (WordNet): definitions + synonyms + prefix suggestions.
export async function searchDictionary(q) {
  const { data } = await api.get('/student/languages/dictionary', { params: { q: q || '' } })
  return data
}

export async function fetchWritingPrompts() {
  const { data } = await api.get('/student/languages/writing')
  return data
}

export async function fetchWritingPrompt(promptId) {
  const { data } = await api.get(`/student/languages/writing/${promptId}`)
  return data
}

export async function submitWritingPrompt(promptId, responseText) {
  const { data } = await api.post(`/student/languages/writing/${promptId}/submit`, {
    response_text: responseText,
  })
  return data
}

export async function fetchSpeakingPrompts() {
  const { data } = await api.get('/student/languages/speaking')
  return data
}

export async function fetchSpeakingPrompt(promptId) {
  const { data } = await api.get(`/student/languages/speaking/${promptId}`)
  return data
}

export async function uploadSpeakingPractice(promptId, blob) {
  const form = new FormData()
  form.append('file', new File([blob], 'speaking.webm', { type: blob.type || 'audio/webm' }))
  const { data } = await api.post(`/student/languages/speaking/${promptId}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 5 * 60 * 1000,
  })
  return data
}

export async function submitSpeakingPractice(promptId, { media_object_id, duration_seconds }) {
  const { data } = await api.post(`/student/languages/speaking/${promptId}/submit`, {
    media_object_id,
    duration_seconds,
  })
  return data
}

export async function fetchSpeakingConversation() {
  const { data } = await api.get('/student/languages/speaking/conversation')
  return data
}

export async function fetchSpeakingConversationProgress() {
  const { data } = await api.get('/student/languages/speaking/conversation/progress')
  return data
}

export async function postSpeakingConversationTurn(blob, durationSeconds, voice, focus) {
  const form = new FormData()
  form.append('file', new File([blob], 'conversation.webm', { type: blob.type || 'audio/webm' }))
  if (durationSeconds != null) form.append('duration_seconds', String(durationSeconds))
  if (voice) form.append('tts_voice', String(voice))
  if (focus) form.append('focus', String(focus))
  const { data } = await api.post('/student/languages/speaking/conversation/turn', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90 * 1000,
  })
  return data
}

export async function resetSpeakingConversation() {
  const { data } = await api.delete('/student/languages/speaking/conversation')
  return data
}

export async function fetchShadowSentences(focus) {
  const { data } = await api.get('/student/languages/speaking/shadow/sentences', {
    params: focus ? { focus } : {},
  })
  return data
}

export async function submitShadow(blob, targetText) {
  const form = new FormData()
  form.append('target_text', String(targetText))
  form.append('file', new File([blob], 'shadow.webm', { type: blob.type || 'audio/webm' }))
  const { data } = await api.post('/student/languages/speaking/shadow', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90 * 1000,
  })
  return data
}

export async function fetchCurriculum() {
  const { data } = await api.get('/student/languages/curriculum')
  return data
}

export async function markObjectivePracticed(objectiveId) {
  const { data } = await api.post('/student/languages/curriculum/objective/practiced', {
    objective_id: objectiveId,
  })
  return data
}

export async function fetchObjectiveLesson(objectiveId) {
  const { data } = await api.get(
    `/student/languages/curriculum/objective/${encodeURIComponent(objectiveId)}/lesson`,
  )
  return data
}

export async function fetchDailyPlan() {
  const { data } = await api.get('/student/languages/daily-plan')
  return data
}

export async function fetchLanguageXp() {
  const { data } = await api.get('/student/languages/xp')
  return data
}

// --- Adaptive difficulty ---
export async function fetchAdaptiveState() {
  const { data } = await api.get('/student/languages/adaptive/state')
  return data
}

// --- Vocabulary spaced repetition (SM-2) stats ---
export async function fetchVocabularyStats() {
  const { data } = await api.get('/student/languages/vocabulary/stats')
  return data
}

// --- Speaking conversation scenarios (role-play) ---
export async function fetchScenarios() {
  const { data } = await api.get('/student/languages/speaking/scenarios')
  return data
}

export async function startScenario(scenarioId) {
  const { data } = await api.post(`/student/languages/speaking/scenarios/${scenarioId}/start`)
  return data
}

export async function fetchScenarioSession(sessionId) {
  const { data } = await api.get(`/student/languages/speaking/scenarios/session/${sessionId}`)
  return data
}

export async function scenarioTurn(sessionId, text) {
  const { data } = await api.post('/student/languages/speaking/scenarios/turn', {
    session_id: sessionId,
    text,
  })
  return data
}

export async function scenarioTurnVoice(sessionId, blob) {
  const form = new FormData()
  form.append('session_id', String(sessionId))
  form.append('file', new File([blob], 'scenario.webm', { type: blob.type || 'audio/webm' }))
  const { data } = await api.post('/student/languages/speaking/scenarios/turn/voice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90 * 1000,
  })
  return data
}

export async function endScenario(sessionId) {
  const { data } = await api.post('/student/languages/speaking/scenarios/end', {
    session_id: sessionId,
  })
  return data
}

export async function fetchLessons() {
  const { data } = await api.get('/student/languages/lessons')
  return data
}

export async function fetchLesson(id) {
  const { data } = await api.get(`/student/languages/lessons/${id}`)
  return data
}

// On-demand detailed explanation of a conversation turn's correction.
export async function fetchConversationTurnExplanation(turnId) {
  const { data } = await api.get(`/student/languages/speaking/conversation/turn/${turnId}/explanation`)
  return data
}

// --- Speaking history (past conversations + scenarios) ---
export async function fetchConversationSessions() {
  const { data } = await api.get('/student/languages/speaking/conversation/sessions')
  return data
}

export async function fetchConversationSessionDetail(sessionId) {
  const { data } = await api.get(`/student/languages/speaking/conversation/sessions/${sessionId}`)
  return data
}

export async function fetchScenarioSessions() {
  const { data } = await api.get('/student/languages/speaking/scenarios/sessions')
  return data
}

export function vocabularyStatusLabel(status) {
  const map = {
    new: 'Not Learned Yet',
    learning: 'Review Later',
    known: 'Known',
  }
  return map[status] || status
}

// --- 4-skill AI placement exam (speaking / listening / reading / writing) ---
export async function initiateExam() {
  const { data } = await api.post('/student/languages/exam/initiate')
  return data
}

export async function fetchExamState(sessionId) {
  const { data } = await api.get(`/student/languages/exam/${sessionId}/state`)
  return data
}

export async function submitSpeakingTurn(
  sessionId,
  blob,
  durationSeconds,
  requestId,
  stateRevision,
  turnToken,
) {
  const form = new FormData()
  form.append('file', new File([blob], 'speaking.webm', { type: blob.type || 'audio/webm' }))
  if (durationSeconds != null) form.append('duration_seconds', String(durationSeconds))
  form.append('request_id', requestId)
  form.append('state_revision', String(stateRevision))
  form.append('turn_token', turnToken)
  const { data } = await api.post(`/student/languages/exam/${sessionId}/speaking/turn`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 2 * 60 * 1000,
  })
  return data
}

export async function answerExamMcq(sessionId, choiceIndex, requestId, stateRevision, questionToken) {
  const { data } = await api.post(`/student/languages/exam/${sessionId}/answer`, {
    choice_index: choiceIndex,
    request_id: requestId,
    state_revision: stateRevision,
    question_token: questionToken,
  })
  return data
}

export async function submitExamWriting(sessionId, text, requestId, stateRevision, promptToken) {
  const { data } = await api.post(`/student/languages/exam/${sessionId}/writing`, {
    text,
    request_id: requestId,
    state_revision: stateRevision,
    prompt_token: promptToken,
  })
  return data
}

export async function fetchExamReport(sessionId) {
  const { data } = await api.get(`/student/languages/exam/${sessionId}/report`)
  return data
}

export async function retryExamEvaluation(sessionId) {
  const { data } = await api.post(`/student/languages/exam/${sessionId}/evaluation/retry`)
  return data
}

export async function abandonExam(sessionId) {
  const { data } = await api.post(`/student/languages/exam/${sessionId}/abandon`)
  return data
}

export async function fetchLanguageCertificates() {
  const { data } = await api.get('/student/languages/certificates')
  return data
}

export async function verifyLanguageCertificate(certificateNumber) {
  const { data } = await api.get(`/verify-certificate/${encodeURIComponent(certificateNumber)}`)
  return data
}

// ---- Adaptive Intelligence Layer (v2) ----
export async function fetchLearnerMemory() {
  const { data } = await api.get('/v2/learner/memory')
  return data
}

export async function updateLearnerMemory(payload) {
  const { data } = await api.put('/v2/learner/memory', payload)
  return data
}

export async function fetchErrorReport() {
  const { data } = await api.get('/v2/learner/errors/report')
  return data
}

export async function fetchDifficultyProfile() {
  const { data } = await api.get('/v2/learner/difficulty')
  return data
}

export async function fetchCoachRecommendation(refresh = false) {
  const { data } = await api.get('/v2/coach/recommendation', { params: { refresh } })
  return data
}

export async function fetchPronunciationTrends() {
  const { data } = await api.get('/v2/pronunciation/trends')
  return data
}

export async function fetchCefrProgress() {
  const { data } = await api.get('/v2/analytics/cefr-progress')
  return data
}

export async function fetchVocabularyGrowth() {
  const { data } = await api.get('/v2/analytics/vocabulary-growth')
  return data
}

// ---- Vocabulary pronunciation (hear + say) ----
export async function sayWord(word) {
  const { data } = await api.post('/student/languages/vocabulary/say', { word })
  return data
}

export async function pronounceWord({ word, blob, durationSeconds }) {
  const form = new FormData()
  form.append('word', word)
  form.append('file', new File([blob], 'word.webm', { type: blob.type || 'audio/webm' }))
  if (durationSeconds != null) form.append('duration_seconds', String(durationSeconds))
  const { data } = await api.post('/student/languages/vocabulary/pronounce', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60 * 1000,
  })
  return data
}

// ---- Offline infinite vocabulary generator ----
export async function fetchVocabGeneratorOptions() {
  const { data } = await api.get('/student/languages/vocabulary/generator/options')
  return data
}

export async function generateVocabBatch({ topic = null, level = null } = {}) {
  const { data } = await api.post('/student/languages/vocabulary/generate-batch', { topic, level })
  return data
}
