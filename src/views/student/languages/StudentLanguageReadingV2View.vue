<template>
  <div class="reading-v2-page slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Reading Practice V2"
      subtitle="AI-generated reading activities controlled by your level, stage, and recent evidence."
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <section v-if="viewMode === 'overview'" class="reading-grid">
        <div class="reading-main">
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <div class="d-flex align-center justify-space-between flex-wrap gap-3">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">Current stage</div>
                <div class="d-flex align-center gap-2 flex-wrap">
                  <v-chip color="secondary" variant="flat" size="large">{{ overview?.current_cefr || 'A1' }}</v-chip>
                  <v-chip color="primary" variant="tonal" size="large">{{ overview?.current_stage || 'Beginner' }}</v-chip>
                  <v-chip v-if="overview?.status" :color="statusColor(overview.status)" variant="tonal">
                    {{ labelize(overview.status) }}
                  </v-chip>
                </div>
              </div>
              <div class="d-flex gap-2 flex-wrap">
                <v-btn
                  color="secondary"
                  variant="flat"
                  size="large"
                  prepend-icon="mdi-play"
                  :loading="startingPractice"
                  @click="startAttempt('practice')"
                >
                  Start Practice
                </v-btn>
                <v-btn
                  v-if="readinessAvailable"
                  color="warning"
                  variant="tonal"
                  size="large"
                  prepend-icon="mdi-flag-checkered"
                  :loading="startingReadiness"
                  @click="startAttempt('readiness')"
                >
                  Readiness Test
                </v-btn>
              </div>
            </div>

            <v-divider class="my-4" />
            <div class="mastery-grid">
              <div>
                <div class="text-caption text-medium-emphasis">Attempts evidenced</div>
                <div class="text-h6 font-weight-bold">{{ mastery.attempts_completed ?? 0 }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Mastery score</div>
                <div class="text-h6 font-weight-bold">{{ mastery.mastery_score ?? 0 }}%</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Evidence status</div>
                <div class="text-h6 font-weight-bold">
                  {{ mastery.evidence_sufficient ? 'Sufficient' : 'Building' }}
                </div>
              </div>
            </div>
          </v-card>

          <v-card class="glass-card pa-5" variant="flat">
            <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
              <div>
                <h3 class="text-subtitle-1 font-weight-bold mb-0">Reading path</h3>
                <p class="text-body-2 text-medium-emphasis mb-0">CEFR levels split into Beginner, Intermediate, and Advanced stages.</p>
              </div>
              <v-chip size="small" variant="tonal" color="secondary">{{ pathStages.length }} stages</v-chip>
            </div>

            <div class="path-map">
              <div v-for="level in cefrLevels" :key="level" class="path-row">
                <div class="path-row__level">{{ level }}</div>
                <div class="path-row__stages">
                  <div
                    v-for="stage in stagesFor(level)"
                    :key="`${stage.cefr_level}-${stage.internal_stage}`"
                    class="stage-pill"
                    :class="`stage-pill--${stageStatus(stage)}`"
                  >
                    <span>{{ stage.internal_stage }}</span>
                    <small>{{ labelize(stageStatus(stage)) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </v-card>
        </div>

        <aside class="reading-side">
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Recent history</h3>
            <div v-if="historyItems.length" class="history-list">
              <div v-for="item in historyItems" :key="item.attempt_id" class="history-item">
                <div>
                  <div class="font-weight-bold">{{ labelize(item.mode) }} · {{ item.cefr_level }} {{ item.internal_stage }}</div>
                  <div class="text-caption text-medium-emphasis">{{ formatDate(item.submitted_at || item.created_at) }}</div>
                </div>
                <v-chip size="small" :color="item.score_percent == null ? 'grey' : scoreColor(item.score_percent)" variant="tonal">
                  {{ item.score_percent == null ? labelize(item.status) : `${item.score_percent}%` }}
                </v-chip>
              </div>
            </div>
            <v-alert v-else type="info" variant="tonal" density="comfortable">
              No Reading V2 attempts yet.
            </v-alert>
          </v-card>

          <v-card class="glass-card pa-5" variant="flat">
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Evidence summary</h3>
            <div v-if="summaryChips.length" class="d-flex flex-wrap gap-2">
              <v-chip v-for="chip in summaryChips" :key="chip.label" size="small" variant="tonal" :color="chip.color">
                {{ chip.label }}: {{ chip.value }}
              </v-chip>
            </div>
            <v-alert v-else type="info" variant="tonal" density="comfortable">
              Evidence will appear after a few generated activities.
            </v-alert>
          </v-card>
        </aside>
      </section>

      <section v-else-if="viewMode === 'practice' && attempt" class="practice-layout">
        <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
          <div>
            <v-chip color="secondary" variant="flat" size="small">{{ attempt.cefr_level }} {{ attempt.internal_stage }}</v-chip>
            <v-chip class="ml-2" color="primary" variant="tonal" size="small">{{ labelize(attempt.mode) }}</v-chip>
          </div>
          <span class="text-caption text-medium-emphasis">{{ answeredCount }} / {{ questions.length }} answered</span>
        </div>

        <v-card class="glass-card pa-6 mb-4" variant="flat">
          <div class="text-caption text-medium-emphasis mb-1">{{ safeActivity.topic }}</div>
          <h2 class="text-h5 font-weight-bold mb-4">{{ safeActivity.title }}</h2>
          <p class="reading-passage" dir="ltr">{{ safeActivity.passage }}</p>
        </v-card>

        <v-card class="glass-card pa-6" variant="flat">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">Questions</h3>
          <div v-for="(question, index) in questions" :key="question.id" class="question-block">
            <div class="d-flex align-start gap-3 mb-3">
              <v-avatar color="secondary" variant="tonal" size="30">{{ index + 1 }}</v-avatar>
              <div>
                <div class="font-weight-bold" dir="ltr">{{ question.stem }}</div>
                <div class="text-caption text-medium-emphasis">{{ questionTypeLabel(question.type) }} · {{ labelize(question.subskill) }}</div>
              </div>
            </div>

            <v-radio-group
              v-if="question.type === 'mcq'"
              v-model="answers[question.id]"
              density="comfortable"
              hide-details
            >
              <v-radio
                v-for="choice in safeChoices(question)"
                :key="choice.id"
                :label="choice.text"
                :value="choice.id"
              />
            </v-radio-group>

            <v-btn-toggle
              v-else-if="question.type === 'true_false'"
              v-model="answers[question.id]"
              color="secondary"
              variant="outlined"
              divided
              mandatory
            >
              <v-btn :value="true">True</v-btn>
              <v-btn :value="false">False</v-btn>
            </v-btn-toggle>

            <v-text-field
              v-else-if="question.type === 'gap_fill'"
              v-model="answers[question.id]"
              label="Your answer"
              variant="outlined"
              density="comfortable"
              hide-details
            />

            <v-textarea
              v-else-if="question.type === 'short_answer'"
              v-model="answers[question.id]"
              label="Short answer"
              variant="outlined"
              density="comfortable"
              rows="2"
              auto-grow
              hide-details
            />

            <v-alert v-else type="warning" variant="tonal" density="compact">
              This question type is not supported in the current frontend skeleton.
            </v-alert>
          </div>

          <v-btn
            color="secondary"
            variant="flat"
            size="large"
            block
            :disabled="!canSubmit"
            :loading="submitting"
            prepend-icon="mdi-check-circle-outline"
            @click="submitAttempt"
          >
            Submit answers
          </v-btn>
        </v-card>
      </section>

      <section v-else-if="viewMode === 'results' && result" class="results-layout">
        <v-card class="glass-card pa-6 mb-4" variant="flat">
          <v-alert :type="result.passed ? 'success' : 'warning'" variant="tonal" class="mb-4">
            Score: <strong>{{ result.score_percent }}%</strong>
            <span v-if="result.next_action"> · {{ labelize(result.next_action) }}</span>
          </v-alert>

          <div v-if="result.question_results?.length" class="result-list">
            <div
              v-for="item in result.question_results"
              :key="item.question_id"
              class="result-item"
              :class="item.correct ? 'result-item--ok' : 'result-item--bad'"
            >
              <v-icon :color="item.correct ? 'success' : 'error'" :icon="item.correct ? 'mdi-check-circle' : 'mdi-close-circle'" />
              <div>
                <div class="font-weight-bold">
                  {{ questionTitle(item.question_id) }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  {{ questionTypeLabel(item.question_type) }} · {{ labelize(item.subskill) }} · {{ item.correct ? 'Correct' : 'Not quite' }}
                </div>
                <div v-if="questionFeedback(item.question_id)" class="text-body-2 mt-1">
                  {{ questionFeedback(item.question_id) }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="resultSummary.length" class="d-flex flex-wrap gap-2 mt-4">
            <v-chip v-for="chip in resultSummary" :key="chip.label" size="small" variant="tonal" color="secondary">
              {{ chip.label }}: {{ chip.value }}
            </v-chip>
          </div>
        </v-card>

        <div class="d-flex flex-wrap gap-2">
          <v-btn color="secondary" variant="tonal" prepend-icon="mdi-view-dashboard-outline" @click="returnToOverview">
            Return to overview
          </v-btn>
          <v-btn color="secondary" variant="flat" prepend-icon="mdi-play" :loading="startingPractice" @click="startAttempt('practice')">
            Next practice
          </v-btn>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { getErrorMessage } from '../../../api/client.js'
import {
  createReadingV2Attempt,
  fetchReadingV2History,
  fetchReadingV2Overview,
  fetchReadingV2Path,
  submitReadingV2Attempt,
} from '../../../api/language.js'

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const SECRET_FIELDS = ['answer_key', 'accepted_answers', 'required_key_terms']

const loading = ref(true)
const loadError = ref('')
const overview = ref(null)
const path = ref(null)
const history = ref(null)
const attempt = ref(null)
const result = ref(null)
const answers = ref({})
const startedAt = ref(null)
const viewMode = ref('overview')
const startingPractice = ref(false)
const startingReadiness = ref(false)
const submitting = ref(false)

const cefrLevels = CEFR_LEVELS
const pathStages = computed(() => path.value?.stages || [])
const historyItems = computed(() => history.value?.attempts || [])
const mastery = computed(() => overview.value?.recent_mastery || {})
const readinessAvailable = computed(() =>
  overview.value?.next_action === 'readiness' || !!overview.value?.readiness_target_level,
)
const safeActivity = computed(() => stripSecrets(attempt.value?.activity || {}))
const questions = computed(() => (safeActivity.value?.questions || []).map(stripSecrets))
const answeredCount = computed(() => questions.value.filter((question) => hasAnswer(question)).length)
const canSubmit = computed(() => questions.value.length > 0 && questions.value.every((question) => hasAnswer(question)))

const summaryChips = computed(() => {
  const chips = []
  const subskills = mastery.value?.subskills || {}
  const questionTypes = mastery.value?.question_types || {}
  for (const [key, value] of Object.entries(subskills).slice(0, 4)) {
    chips.push({ label: labelize(key), value: `${value.score_percent ?? 0}%`, color: 'primary' })
  }
  for (const [key, value] of Object.entries(questionTypes).slice(0, 4)) {
    chips.push({ label: questionTypeLabel(key), value: `${value.score_percent ?? 0}%`, color: 'secondary' })
  }
  return chips
})

const resultSummary = computed(() => {
  const byType = new Map()
  for (const item of result.value?.question_results || []) {
    const current = byType.get(item.question_type) || { correct: 0, total: 0 }
    current.total += 1
    if (item.correct) current.correct += 1
    byType.set(item.question_type, current)
  }
  return [...byType.entries()].map(([type, counts]) => ({
    label: questionTypeLabel(type),
    value: `${counts.correct}/${counts.total}`,
  }))
})

onMounted(loadOverview)

async function loadOverview() {
  loading.value = true
  loadError.value = ''
  try {
    const [overviewData, pathData, historyData] = await Promise.all([
      fetchReadingV2Overview(),
      fetchReadingV2Path(),
      fetchReadingV2History(),
    ])
    overview.value = overviewData
    path.value = pathData
    history.value = historyData
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to load Reading Practice V2')
  } finally {
    loading.value = false
  }
}

async function startAttempt(mode) {
  if (mode === 'readiness') startingReadiness.value = true
  else startingPractice.value = true
  loadError.value = ''
  try {
    const data = await createReadingV2Attempt(mode)
    attempt.value = sanitizeAttempt(data)
    result.value = null
    answers.value = {}
    startedAt.value = Date.now()
    viewMode.value = 'practice'
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not start reading practice')
  } finally {
    startingPractice.value = false
    startingReadiness.value = false
  }
}

async function submitAttempt() {
  if (!attempt.value || !canSubmit.value || submitting.value) return
  submitting.value = true
  loadError.value = ''
  try {
    const duration = startedAt.value ? Math.max(0, Math.round((Date.now() - startedAt.value) / 1000)) : null
    result.value = await submitReadingV2Attempt(attempt.value.attempt_id, buildSubmitAnswers(), duration)
    viewMode.value = 'results'
    await refreshHistoryOnly()
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to submit reading answers')
  } finally {
    submitting.value = false
  }
}

async function returnToOverview() {
  viewMode.value = 'overview'
  attempt.value = null
  result.value = null
  answers.value = {}
  await loadOverview()
}

async function refreshHistoryOnly() {
  try {
    history.value = await fetchReadingV2History()
  } catch {
    /* non-fatal */
  }
}

function buildSubmitAnswers() {
  const out = {}
  for (const question of questions.value) {
    const value = answers.value[question.id]
    if (question.type === 'mcq') out[question.id] = { choice_id: value }
    else out[question.id] = value
  }
  return out
}

function hasAnswer(question) {
  const value = answers.value[question.id]
  if (typeof value === 'boolean') return true
  if (typeof value === 'number') return true
  if (typeof value === 'string') return value.trim().length > 0
  return value !== undefined && value !== null
}

function stripSecrets(value) {
  if (Array.isArray(value)) return value.map(stripSecrets)
  if (!value || typeof value !== 'object') return value
  const clean = {}
  for (const [key, nested] of Object.entries(value)) {
    if (SECRET_FIELDS.includes(key)) continue
    clean[key] = stripSecrets(nested)
  }
  return clean
}

function sanitizeAttempt(payload) {
  return stripSecrets(payload || {})
}

function safeChoices(question) {
  return (question.choices || []).map(stripSecrets)
}

function stagesFor(level) {
  return pathStages.value.filter((stage) => stage.cefr_level === level)
}

function stageStatus(stage) {
  return stage.status || 'locked'
}

function statusColor(status) {
  const map = {
    active: 'success',
    current: 'secondary',
    unlocked: 'primary',
    completed: 'success',
    mastered: 'success',
    locked: 'grey',
  }
  return map[status] || 'grey'
}

function scoreColor(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

function labelize(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function questionTypeLabel(type) {
  const map = {
    mcq: 'MCQ',
    true_false: 'True / False',
    gap_fill: 'Gap Fill',
    short_answer: 'Short Answer',
  }
  return map[type] || labelize(type || 'Question')
}

function questionById(questionId) {
  return questions.value.find((question) => question.id === questionId) || null
}

function questionTitle(questionId) {
  return questionById(questionId)?.stem || `Question ${questionId}`
}

function questionFeedback(questionId) {
  const question = questionById(questionId)
  return question?.explanation || question?.feedback || ''
}

function formatDate(iso) {
  if (!iso) return 'Not submitted'
  try {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return iso
  }
}
</script>

<style scoped>
.reading-v2-page {
  max-width: 1180px;
  margin: 0 auto;
}

.reading-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  align-items: start;
}

.mastery-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.path-map {
  display: grid;
  gap: 12px;
}

.path-row {
  display: grid;
  grid-template-columns: 56px 1fr;
  align-items: center;
  gap: 12px;
}

.path-row__level {
  font-weight: 800;
  color: rgb(var(--v-theme-secondary));
}

.path-row__stages {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.stage-pill {
  min-height: 64px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  background: rgba(var(--v-theme-surface), 0.52);
}

.stage-pill span {
  font-weight: 700;
  line-height: 1.2;
}

.stage-pill small {
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.stage-pill--current {
  border-color: rgba(var(--v-theme-secondary), 0.75);
  background: rgba(var(--v-theme-secondary), 0.13);
}

.stage-pill--unlocked {
  border-color: rgba(var(--v-theme-primary), 0.5);
  background: rgba(var(--v-theme-primary), 0.08);
}

.stage-pill--completed,
.stage-pill--mastered {
  border-color: rgba(var(--v-theme-success), 0.55);
  background: rgba(var(--v-theme-success), 0.1);
}

.stage-pill--locked {
  opacity: 0.62;
}

.history-list,
.result-list {
  display: grid;
  gap: 10px;
}

.history-item,
.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  padding: 12px;
}

.practice-layout,
.results-layout {
  max-width: 920px;
  margin: 0 auto;
}

.reading-passage {
  white-space: pre-wrap;
  line-height: 1.85;
  font-size: 1rem;
}

.question-block {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.result-item {
  justify-content: flex-start;
  align-items: flex-start;
}

.result-item--ok {
  border-color: rgba(var(--v-theme-success), 0.35);
  background: rgba(var(--v-theme-success), 0.08);
}

.result-item--bad {
  border-color: rgba(var(--v-theme-error), 0.3);
  background: rgba(var(--v-theme-error), 0.07);
}

@media (max-width: 900px) {
  .reading-grid {
    grid-template-columns: 1fr;
  }

  .reading-side {
    order: 2;
  }
}

@media (max-width: 640px) {
  .mastery-grid,
  .path-row__stages {
    grid-template-columns: 1fr;
  }

  .path-row {
    grid-template-columns: 1fr;
  }
}
</style>
