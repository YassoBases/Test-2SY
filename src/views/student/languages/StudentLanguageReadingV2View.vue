<template>
  <div class="reading-v2-page slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Reading Practice"
      subtitle="Practice with reading activities matched to your level and progress."
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
                <div class="readiness-inline mt-3">
                  <v-chip size="small" :color="readinessColor" variant="tonal">
                    {{ readinessStatusLabel }}
                  </v-chip>
                  <span>{{ readinessInlineText }}</span>
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
                <div class="text-caption text-medium-emphasis">Current level</div>
                <div class="text-h6 font-weight-bold">{{ overview?.current_cefr || 'A1' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Current stage</div>
                <div class="text-h6 font-weight-bold">{{ overview?.current_stage || 'Beginner' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Mastery score</div>
                <div class="text-h6 font-weight-bold">{{ formatPercent(displayedMasteryScore) }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Readiness</div>
                <div class="text-h6 font-weight-bold">
                  {{ overview?.readiness_available ? 'Available' : 'Locked' }}
                </div>
              </div>
            </div>
          </v-card>

          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
              <div>
                <h3 class="text-subtitle-1 font-weight-bold mb-0">Current-stage evidence</h3>
                <p class="text-body-2 text-medium-emphasis mb-0">
                  Progress is based on recent practice evidence, not XP alone.
                </p>
              </div>
              <v-chip :color="currentStageEvidence.mastered ? 'success' : 'warning'" size="small" variant="tonal">
                {{ currentStageEvidence.mastered ? 'Stage mastered' : 'Still building' }}
              </v-chip>
            </div>

            <div class="evidence-list">
              <div v-for="metric in evidenceMetrics" :key="metric.label" class="evidence-row">
                <v-icon :color="metric.met ? 'success' : 'warning'" :icon="metric.met ? 'mdi-check-circle' : 'mdi-clock-outline'" />
                <div>
                  <div class="font-weight-bold">{{ metric.label }}</div>
                  <div class="text-caption text-medium-emphasis">{{ metric.value }}</div>
                </div>
              </div>
            </div>

            <div v-if="weakestSubskills.length" class="mt-4">
              <div class="text-caption text-medium-emphasis mb-2">Weakest subskills</div>
              <div class="d-flex flex-wrap gap-2">
                <v-chip v-for="item in weakestSubskills" :key="item.name" color="warning" size="small" variant="tonal">
                  {{ labelize(item.name) }}: {{ formatPercent(item.score) }}
                </v-chip>
              </div>
            </div>

            <v-alert v-if="currentBlockingReasonTexts.length" type="warning" variant="tonal" density="comfortable" class="mt-4">
              <div class="font-weight-bold mb-1">To unlock the next step</div>
              <ul class="reason-list">
                <li v-for="reason in currentBlockingReasonTexts" :key="reason">{{ reason }}</li>
              </ul>
            </v-alert>
            <v-alert v-else type="success" variant="tonal" density="comfortable" class="mt-4">
              This stage has enough evidence for progression.
            </v-alert>
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
                    <div class="stage-pill__top">
                      <span>{{ stage.internal_stage }}</span>
                      <v-icon :icon="stageIcon(stage)" :color="statusColor(stageStatus(stage))" size="18" />
                    </div>
                    <small>{{ stageStatusLabel(stage) }}</small>
                    <p v-if="stageReason(stage)" class="stage-pill__reason">{{ stageReason(stage) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </v-card>
        </div>

        <aside class="reading-side">
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <div class="d-flex align-center justify-space-between gap-2 mb-3">
              <h3 class="text-subtitle-1 font-weight-bold mb-0">Readiness test</h3>
              <v-chip :color="readinessColor" size="small" variant="tonal">{{ readinessStatusLabel }}</v-chip>
            </div>
            <div class="readiness-detail">
              <div>
                <span class="text-caption text-medium-emphasis">Target</span>
                <strong>{{ readinessTargetText }}</strong>
              </div>
              <div>
                <span class="text-caption text-medium-emphasis">Status</span>
                <strong>{{ readinessDetailText }}</strong>
              </div>
            </div>
            <v-alert
              v-if="!overview?.readiness_available"
              type="info"
              variant="tonal"
              density="comfortable"
              class="mt-3"
            >
              {{ readinessBlockedText }}
            </v-alert>
            <div v-if="retakeStatus?.blocked" class="retake-meter mt-3">
              <div class="d-flex justify-space-between text-caption text-medium-emphasis mb-1">
                <span>Advanced practices before retake</span>
                <span>{{ retakeStatus.completed_additional_practice || 0 }} / {{ retakeStatus.required_additional_practice || 3 }}</span>
              </div>
              <v-progress-linear
                color="warning"
                height="8"
                rounded
                :model-value="retakeProgress"
              />
            </div>
          </v-card>

          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Recent history</h3>
            <div v-if="historyItems.length" class="history-list">
              <div v-for="item in historyItems" :key="item.attempt_id" class="history-item">
                <div>
                  <div class="font-weight-bold">{{ labelize(item.mode) }} · {{ item.cefr_level }} {{ item.internal_stage }}</div>
                  <div class="text-caption text-medium-emphasis">{{ historyDateLabel(item) }}</div>
                </div>
                <v-chip size="small" :color="historyChipColor(item)" variant="tonal">
                  {{ historyStatusLabel(item) }}
                </v-chip>
              </div>
            </div>
            <v-alert v-else type="info" variant="tonal" density="comfortable">
              No reading practice attempts yet.
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

        <v-card class="glass-card pa-6 mb-4 reading-v2-text" variant="flat">
          <div class="text-caption text-medium-emphasis mb-1">{{ safeActivity.topic }}</div>
          <h2 class="text-h5 font-weight-bold mb-4">{{ safeActivity.title }}</h2>
          <p class="reading-passage">{{ safeActivity.passage }}</p>
        </v-card>

        <v-card class="glass-card pa-6 reading-v2-text" variant="flat">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">Questions</h3>
          <div v-for="(question, index) in questions" :key="question.id" class="question-block">
            <div class="d-flex align-start gap-3 mb-3">
              <v-avatar color="secondary" variant="tonal" size="30">{{ index + 1 }}</v-avatar>
              <div>
                <div class="font-weight-bold question-stem">{{ displayQuestionStem(question) }}</div>
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

            <div
              v-else-if="question.type === 'gap_fill' && gapFillParts(question)"
              class="gap-fill-inline"
            >
              <span>{{ gapFillParts(question).before }}</span>
              <input
                v-model="answers[question.id]"
                class="gap-fill-inline__input"
                type="text"
                :aria-label="`Answer for question ${index + 1}`"
                autocomplete="off"
              />
              <span>{{ gapFillParts(question).after }}</span>
            </div>

            <v-text-field
              v-else-if="question.type === 'gap_fill'"
              v-model="answers[question.id]"
              label="Your answer"
              class="reading-answer-field"
              variant="outlined"
              density="comfortable"
              hide-details
            />

            <v-textarea
              v-else-if="question.type === 'short_answer'"
              v-model="answers[question.id]"
              label="Short answer"
              class="reading-answer-field"
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
        <v-card class="glass-card pa-6 mb-4 reading-v2-text" variant="flat">
          <v-alert :type="result.passed ? 'success' : 'warning'" variant="tonal" class="mb-4 reading-v2-text">
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
                <div v-if="item.correct && questionFeedback(item.question_id)" class="text-body-2 mt-1 result-feedback">
                  {{ questionFeedback(item.question_id) }}
                </div>
                <div v-if="!item.correct" class="result-answer-details">
                  <div v-if="item.student_answer" class="result-answer-details__row">
                    <span>Your answer</span>
                    <strong>{{ item.student_answer }}</strong>
                  </div>
                  <div v-if="item.expected_answer" class="result-answer-details__row">
                    <span>Expected answer</span>
                    <strong>{{ item.expected_answer }}</strong>
                  </div>
                  <div v-if="resultExplanation(item)" class="result-answer-details__explanation">
                    {{ resultExplanation(item) }}
                  </div>
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
const INTERNAL_STAGES = ['Beginner', 'Intermediate', 'Advanced']
const SECRET_FIELDS = ['answer_key', 'accepted_answers', 'required_key_terms']
const STAGE_REQUIREMENTS = {
  attempts: 5,
  uniqueActivities: 4,
  questions: 12,
  questionTypes: 3,
  recentAverage: 80,
  recentAttemptMinimum: 70,
  coreSubskill: 70,
}

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
const currentStageEvidence = computed(() => mastery.value?.current_stage_evidence || {})
const readinessGate = computed(() => mastery.value?.readiness || {})
const retakeStatus = computed(() => readinessGate.value?.retake || null)
const readinessAvailable = computed(() => overview.value?.readiness_available === true)
const displayedMasteryScore = computed(() =>
  currentStageEvidence.value?.recent_average_score ?? mastery.value?.mastery_score ?? 0,
)
const readinessTargetLevel = computed(() =>
  overview.value?.readiness_target_level || readinessGate.value?.target_level || nextCefr(overview.value?.current_cefr),
)
const readinessTargetText = computed(() =>
  readinessTargetLevel.value ? `${readinessTargetLevel.value} readiness` : 'No next level',
)
const readinessColor = computed(() => {
  if (overview.value?.status === 'mastered') return 'success'
  return readinessAvailable.value ? 'warning' : 'grey'
})
const readinessStatusLabel = computed(() => {
  if (overview.value?.status === 'mastered') return 'Mastered'
  return readinessAvailable.value ? 'Available' : 'Locked'
})
const readinessBlockedText = computed(() => {
  if (readinessAvailable.value) return 'Readiness is available now.'
  return friendlyReason(overview.value?.readiness_blocked_reason || readinessGate.value?.blocked_reason, {
    targetLevel: readinessTargetLevel.value,
    retake: retakeStatus.value,
  })
})
const readinessInlineText = computed(() => {
  if (readinessAvailable.value) return `${readinessTargetText.value} is ready.`
  return readinessBlockedText.value
})
const readinessDetailText = computed(() => {
  if (readinessAvailable.value) return 'Unlocked after Advanced mastery'
  return readinessBlockedText.value
})
const retakeProgress = computed(() => {
  const required = Number(retakeStatus.value?.required_additional_practice || 0)
  if (!required) return 0
  return Math.min(100, Math.round((Number(retakeStatus.value?.completed_additional_practice || 0) / required) * 100))
})
const evidenceMetrics = computed(() => {
  const evidence = currentStageEvidence.value
  const questionTypes = evidence.question_types_represented || []
  const recentLowest = Number(evidence.recent_lowest_score || 0)
  const hasRecentWindow = (evidence.recent_attempt_ids || []).length >= 5
  return [
    {
      label: 'Practice attempts',
      value: `${Number(evidence.attempts_submitted || 0)} / ${STAGE_REQUIREMENTS.attempts}`,
      met: evidence.requirements?.min_5_submitted_practice_attempts === true,
    },
    {
      label: 'Unique activities',
      value: `${Number(evidence.unique_generated_activities || 0)} / ${STAGE_REQUIREMENTS.uniqueActivities}`,
      met: evidence.requirements?.min_4_unique_generated_activities === true,
    },
    {
      label: 'Answered questions',
      value: `${Number(evidence.total_answered_questions || 0)} / ${STAGE_REQUIREMENTS.questions}`,
      met: evidence.requirements?.min_12_answered_questions === true,
    },
    {
      label: 'Question types',
      value: `${questionTypes.length} / ${STAGE_REQUIREMENTS.questionTypes}${questionTypes.length ? ` (${questionTypes.map(questionTypeLabel).join(', ')})` : ''}`,
      met: evidence.requirements?.min_3_question_types === true,
    },
    {
      label: 'Recent 5-attempt average',
      value: `${formatPercent(evidence.recent_average_score)} needed: ${STAGE_REQUIREMENTS.recentAverage}%`,
      met: evidence.requirements?.recent_5_average_at_least_80 === true,
    },
    {
      label: 'Recent low score check',
      value: hasRecentWindow
        ? recentLowest < STAGE_REQUIREMENTS.recentAttemptMinimum
          ? `One recent attempt is below ${STAGE_REQUIREMENTS.recentAttemptMinimum}%`
          : `No recent attempt below ${STAGE_REQUIREMENTS.recentAttemptMinimum}%`
        : 'Needs 5 recent attempts',
      met: evidence.requirements?.no_recent_attempt_below_70 === true,
    },
  ]
})
const weakestSubskills = computed(() => {
  const scores = currentStageEvidence.value?.core_subskill_scores || {}
  return Object.entries(scores)
    .map(([name, score]) => ({ name, score: Number(score || 0) }))
    .filter((item) => item.score < STAGE_REQUIREMENTS.coreSubskill)
    .sort((a, b) => a.score - b.score)
})
const currentBlockingReasonTexts = computed(() =>
  (currentStageEvidence.value?.blocking_reasons || []).map((reason) =>
    friendlyReason(reason, { weakestSubskill: weakestSubskills.value[0]?.name }),
  ),
)
const safeActivity = computed(() => stripSecrets(attempt.value?.activity || {}))
const questions = computed(() => (safeActivity.value?.questions || []).map(stripSecrets))
const answeredCount = computed(() => questions.value.filter((question) => hasAnswer(question)).length)
const canSubmit = computed(() => questions.value.length > 0 && questions.value.every((question) => hasAnswer(question)))

const summaryChips = computed(() => {
  const chips = []
  const subskills = currentStageEvidence.value?.subskills || {}
  const questionTypes = currentStageEvidence.value?.question_types || {}
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
    loadError.value = getErrorMessage(e, 'Unable to load Reading Practice')
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
  return pathStages.value
    .filter((stage) => stage.cefr_level === level)
    .sort((a, b) => INTERNAL_STAGES.indexOf(a.internal_stage) - INTERNAL_STAGES.indexOf(b.internal_stage))
}

function stageStatus(stage) {
  return stage.status || 'locked'
}

function stageStatusLabel(stage) {
  const map = {
    locked: 'Locked',
    unlocked: 'Unlocked',
    current: 'Current',
    completed: 'Completed',
    mastered: 'Mastered',
  }
  return map[stageStatus(stage)] || labelize(stageStatus(stage))
}

function stageIcon(stage) {
  const map = {
    locked: 'mdi-lock-outline',
    unlocked: 'mdi-lock-open-variant-outline',
    current: 'mdi-map-marker-circle',
    completed: 'mdi-check-circle-outline',
    mastered: 'mdi-check-circle',
  }
  return map[stageStatus(stage)] || 'mdi-circle-outline'
}

function stageReason(stage) {
  const status = stageStatus(stage)
  if (status === 'mastered' || status === 'completed') return 'Evidence complete.'
  if (status === 'unlocked') return 'Ready when you reach this step.'
  const reason = stage.recent_mastery?.locked_reason
  if (status === 'current') {
    const firstBlocker = currentStageEvidence.value?.blocking_reasons?.[0]
    return firstBlocker ? friendlyReason(firstBlocker, { weakestSubskill: weakestSubskills.value[0]?.name }) : ''
  }
  if (stage.cefr_level !== overview.value?.current_cefr && stage.rank > currentRank.value) {
    return 'Pass the readiness test to unlock this level.'
  }
  return friendlyReason(reason || 'previous_stage_not_mastered')
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

const currentRank = computed(() => stageRank(overview.value?.current_cefr || 'A1', overview.value?.current_stage || 'Beginner'))

function stageRank(cefr, stage) {
  return CEFR_LEVELS.indexOf(cefr) * INTERNAL_STAGES.length + INTERNAL_STAGES.indexOf(stage)
}

function nextCefr(cefr) {
  const index = CEFR_LEVELS.indexOf(cefr)
  return index >= 0 && index + 1 < CEFR_LEVELS.length ? CEFR_LEVELS[index + 1] : null
}

function scoreColor(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

function formatPercent(value) {
  const number = Number(value || 0)
  return `${Number.isInteger(number) ? number : number.toFixed(1)}%`
}

function labelize(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function friendlyReason(reason, context = {}) {
  const weakSubskill = context.weakestSubskill ? `: ${labelize(context.weakestSubskill)}` : ''
  const retake = context.retake || {}
  const target = context.targetLevel ? `${context.targetLevel} readiness test` : 'the readiness test'
  const currentLevel = overview.value?.current_cefr || 'this level'
  const remaining = Number(retake.remaining_additional_practice || 0)
  const map = {
    min_5_submitted_practice_attempts: 'Complete more practice attempts.',
    min_4_unique_generated_activities: 'Practice with more unique reading activities.',
    min_12_answered_questions: 'Answer more reading questions.',
    min_3_question_types: 'Try more question types.',
    recent_5_average_at_least_80: 'Improve your recent 5-attempt average to 80%.',
    no_recent_attempt_below_70: 'Keep every recent attempt at 70% or higher.',
    each_core_subskill_at_least_70: `Strengthen weak subskill${weakSubskill}.`,
    no_core_subskill_two_recent_failures_below_60: 'Avoid repeated low scores in core subskills.',
    previous_stage_not_mastered: 'Complete the previous stage first.',
    advanced_stage_not_mastered: `Complete ${currentLevel} Advanced to unlock the ${target}.`,
    current_stage_is_not_advanced: 'Reach Advanced before taking readiness.',
    readiness_retake_requires_more_practice:
      remaining > 0
        ? `Complete ${remaining} more Advanced practice ${remaining === 1 ? 'attempt' : 'attempts'} before retaking readiness.`
        : 'Complete more Advanced practice before retaking readiness.',
    reading_v2_mastered: 'Reading practice is mastered.',
    overall_score_at_least_80: 'Score 80% or higher on readiness.',
    mvp_equivalent_evidence: 'Complete enough readiness evidence.',
    all_mvp_question_types_represented: 'Complete all required question types.',
    each_tested_core_subskill_at_least_70: 'Score at least 70% in each tested core subskill.',
    no_question_type_below_60: 'Keep every question type score at 60% or higher.',
  }
  return map[reason] || 'Keep practicing to unlock this step.'
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

function hasBlank(value) {
  return /_{2,}|\[[^\]]*blank[^\]]*\]|\(\s*blank\s*\)/i.test(String(value || ''))
}

function blankPattern() {
  return /_{2,}|\[[^\]]*blank[^\]]*\]|\(\s*blank\s*\)/i
}

function isGenericGapFillStem(value) {
  return /^answer this gap fill question/i.test(String(value || '').trim())
}

function displayQuestionStem(question) {
  if (question?.type === 'gap_fill') {
    return gapFillPrompt(question) ? 'Fill in the blank.' : 'Complete the sentence.'
  }
  return question?.stem || ''
}

function gapFillPrompt(question) {
  if (!question || question.type !== 'gap_fill') return ''
  const candidate =
    question.sentence_with_blank ||
    question.display_sentence ||
    question.blank_prompt ||
    (!isGenericGapFillStem(question.stem) ? question.stem : '')
  if (hasBlank(candidate)) return candidate
  return 'Use one word or phrase that makes the sentence correct.'
}

function gapFillParts(question) {
  const prompt = gapFillPrompt(question)
  const match = blankPattern().exec(prompt)
  if (!match) return null
  return {
    before: prompt.slice(0, match.index),
    after: prompt.slice(match.index + match[0].length),
  }
}

function questionById(questionId) {
  return questions.value.find((question) => question.id === questionId) || null
}

function questionTitle(questionId) {
  const question = questionById(questionId)
  return question ? displayQuestionStem(question) : `Question ${questionId}`
}

function questionFeedback(questionId) {
  const question = questionById(questionId)
  return question?.explanation || question?.feedback || ''
}

function resultExplanation(item) {
  return item?.explanation || questionFeedback(item?.question_id)
}

function formatDate(iso) {
  if (!iso) return 'Not submitted'
  try {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return iso
  }
}

function isSubmittedHistoryItem(item) {
  return item?.status === 'submitted' && item.score_percent != null
}

function historyStatusLabel(item) {
  if (isSubmittedHistoryItem(item)) return `${item.score_percent}%`
  return 'Not submitted'
}

function historyChipColor(item) {
  return isSubmittedHistoryItem(item) ? scoreColor(item.score_percent) : 'grey'
}

function historyDateLabel(item) {
  if (isSubmittedHistoryItem(item)) return formatDate(item.submitted_at)
  return item?.created_at ? `Started ${formatDate(item.created_at)}` : 'Not submitted'
}
</script>

<style scoped>
.reading-v2-page {
  max-width: 1180px;
  margin: 0 auto;
  direction: ltr;
  text-align: left;
  unicode-bidi: isolate;
}

.reading-v2-text,
.reading-v2-text :deep(*) {
  direction: ltr;
  text-align: left;
}

.reading-v2-page :deep(.v-alert),
.reading-v2-page :deep(.v-chip),
.reading-v2-page :deep(.v-label),
.reading-v2-page :deep(.v-field__input),
.reading-v2-page :deep(.v-radio),
.reading-v2-page :deep(.v-selection-control),
.reading-v2-page :deep(.v-selection-control__wrapper),
.reading-v2-page :deep(.v-selection-control__input),
.reading-v2-page :deep(.v-selection-control__label) {
  direction: ltr;
  text-align: left;
}

.reading-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  align-items: start;
}

.mastery-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.readiness-inline {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  color: rgba(var(--v-theme-on-surface), 0.72);
  font-size: 0.875rem;
  direction: ltr;
  text-align: left;
}

.evidence-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.evidence-row {
  min-height: 72px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  padding: 12px;
  background: rgba(var(--v-theme-surface), 0.42);
  direction: ltr;
  text-align: left;
}

.reason-list {
  margin: 0;
  padding-inline-start: 18px;
}

.readiness-detail {
  display: grid;
  gap: 10px;
  direction: ltr;
  text-align: left;
}

.readiness-detail > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  padding-bottom: 8px;
}

.path-map {
  display: grid;
  gap: 12px;
  direction: ltr;
  text-align: left;
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
  direction: ltr;
}

.stage-pill {
  min-height: 96px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 4px;
  background: rgba(var(--v-theme-surface), 0.52);
  direction: ltr;
  text-align: left;
}

.stage-pill__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.stage-pill span {
  font-weight: 700;
  line-height: 1.2;
}

.stage-pill small {
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.stage-pill__reason {
  margin: 2px 0 0;
  color: rgba(var(--v-theme-on-surface), 0.72);
  font-size: 0.78rem;
  line-height: 1.3;
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
  direction: ltr;
  text-align: left;
}

.question-stem,
.gap-fill-prompt,
.result-feedback {
  direction: ltr;
  text-align: left;
}

.gap-fill-prompt {
  margin: -4px 0 12px 42px;
  color: rgba(var(--v-theme-on-surface), 0.76);
  font-size: 0.95rem;
  line-height: 1.5;
}

.gap-fill-inline {
  margin: -2px 0 12px 42px;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
  color: rgba(var(--v-theme-on-surface), 0.82);
  font-size: 1rem;
  line-height: 1.7;
  direction: ltr;
  text-align: left;
}

.gap-fill-inline__input {
  width: min(190px, 100%);
  min-width: 110px;
  border: 0;
  border-bottom: 2px solid rgba(var(--v-theme-secondary), 0.68);
  border-radius: 0;
  background: rgba(var(--v-theme-secondary), 0.08);
  color: rgb(var(--v-theme-on-surface));
  font: inherit;
  font-weight: 700;
  line-height: 1.4;
  padding: 2px 8px;
  direction: ltr;
  text-align: left;
  outline: none;
}

.gap-fill-inline__input:focus {
  border-bottom-color: rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.14);
}

.question-block {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  direction: ltr;
  text-align: left;
}

.question-block :deep(.v-radio),
.question-block :deep(.v-selection-control),
.question-block :deep(.v-selection-control__label),
.reading-answer-field :deep(.v-field__input),
.reading-answer-field :deep(textarea),
.reading-answer-field :deep(input) {
  direction: ltr;
  text-align: left;
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

.result-answer-details {
  display: grid;
  gap: 6px;
  margin-top: 10px;
  direction: ltr;
  text-align: left;
}

.result-answer-details__row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 0.875rem;
}

.result-answer-details__row span {
  color: rgba(var(--v-theme-on-surface), 0.64);
  min-width: 104px;
}

.result-answer-details__explanation {
  color: rgba(var(--v-theme-on-surface), 0.76);
  font-size: 0.9rem;
  line-height: 1.45;
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
  .evidence-list,
  .path-row__stages {
    grid-template-columns: 1fr;
  }

  .path-row {
    grid-template-columns: 1fr;
  }
}
</style>
