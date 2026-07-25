<template>
  <div class="reading-v2-page slide-up-enter-active">
    <LanguageModuleTabs />
    <PageHeader
      compact
      eyebrow="Learn languages"
      eyebrow-icon="mdi-book-open-page-variant"
      title="Reading Practice"
      subtitle="One stage at a time — practice, gather evidence, unlock the next."
    />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <section v-if="viewMode === 'overview'" class="reading-overview">
        <!-- Mission hero -->
        <div class="mission-hero glass-card">
          <div class="mission-hero__glow" aria-hidden="true" />
          <div class="mission-hero__badge" :data-status="overview?.status || 'active'">
            <span class="mission-hero__cefr">{{ overview?.current_cefr || 'A1' }}</span>
            <span class="mission-hero__stage">{{ overview?.current_stage || 'Beginner' }}</span>
          </div>
          <div class="mission-hero__copy">
            <p class="mission-hero__kicker mb-1">Your reading stage</p>
            <h2 class="mission-hero__title">
              {{ currentStageLabel }}
              <v-chip
                v-if="overview?.status"
                class="ml-2"
                size="small"
                :color="statusColor(overview.status)"
                variant="tonal"
              >
                {{ labelize(overview.status) }}
              </v-chip>
            </h2>
            <p class="mission-hero__hint mb-0">{{ readinessInlineText }}</p>
            <div class="mission-hero__stats">
              <div class="mission-stat">
                <span class="mission-stat__value">{{ formatPercent(displayedMasteryScore) }}</span>
                <span class="mission-stat__label">Mastery</span>
              </div>
              <div class="mission-stat">
                <span class="mission-stat__value">{{ evidenceMetCount }}/{{ evidenceTotalCount }}</span>
                <span class="mission-stat__label">Evidence</span>
              </div>
              <div class="mission-stat">
                <span class="mission-stat__value">{{ readinessStatusLabel }}</span>
                <span class="mission-stat__label">Readiness</span>
              </div>
            </div>
          </div>
          <div class="mission-hero__actions">
            <v-btn
              color="secondary"
              variant="flat"
              size="large"
              rounded="lg"
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
              rounded="lg"
              prepend-icon="mdi-flag-checkered"
              :loading="startingReadiness"
              @click="startAttempt('readiness')"
            >
              Readiness Test
            </v-btn>
          </div>
        </div>

        <div class="reading-grid">
          <div class="reading-main">
            <!-- Evidence as progress story -->
            <div class="evidence-panel glass-card">
              <div class="evidence-panel__head">
                <div class="evidence-ring" :style="{ '--p': evidenceProgressPercent }">
                  <span>{{ evidenceProgressPercent }}%</span>
                </div>
                <div class="min-w-0">
                  <h3 class="evidence-panel__title">Stage evidence</h3>
                  <p class="evidence-panel__sub mb-0">
                    {{ currentStageEvidence.mastered ? 'Stage mastered — ready to move on.' : 'Build proof through practice, not XP.' }}
                  </p>
                  <v-chip
                    class="mt-2"
                    size="small"
                    :color="currentStageEvidence.mastered ? 'success' : 'warning'"
                    variant="tonal"
                  >
                    {{ currentStageEvidence.mastered ? 'Stage mastered' : 'Still building' }}
                  </v-chip>
                </div>
              </div>

              <div class="evidence-checklist">
                <div
                  v-for="metric in evidenceMetrics"
                  :key="metric.label"
                  class="evidence-check"
                  :class="{ 'evidence-check--met': metric.met }"
                  :title="metric.value"
                >
                  <v-icon
                    size="18"
                    :color="metric.met ? 'success' : 'warning'"
                    :icon="metric.met ? 'mdi-check-circle' : 'mdi-circle-outline'"
                  />
                  <span class="evidence-check__label">{{ metric.label }}</span>
                  <span class="evidence-check__value">{{ metric.value }}</span>
                </div>
              </div>

              <div v-if="weakestSubskills.length || underSampledSubskills.length" class="evidence-tags">
                <div v-if="weakestSubskills.length" class="evidence-tags__group">
                  <span class="evidence-tags__label">Focus</span>
                  <v-chip
                    v-for="item in weakestSubskills"
                    :key="item.name"
                    color="warning"
                    size="small"
                    variant="tonal"
                  >
                    {{ labelize(item.name) }} {{ formatPercent(item.score) }}
                  </v-chip>
                </div>
                <div v-if="underSampledSubskills.length" class="evidence-tags__group">
                  <span class="evidence-tags__label">Need more</span>
                  <v-chip
                    v-for="item in underSampledSubskills"
                    :key="item.name"
                    color="info"
                    size="small"
                    variant="tonal"
                  >
                    {{ labelize(item.name) }} {{ Number(item.total || 0) }}/{{ item.required_questions || 3 }}
                  </v-chip>
                </div>
              </div>

              <v-alert
                v-if="currentBlockingReasonTexts.length"
                type="warning"
                variant="tonal"
                density="comfortable"
                class="mt-4"
              >
                <div class="font-weight-bold mb-1">To unlock the next step</div>
                <ul class="reason-list">
                  <li v-for="reason in currentBlockingReasonTexts" :key="reason">{{ reason }}</li>
                </ul>
              </v-alert>
              <v-alert v-else type="success" variant="tonal" density="comfortable" class="mt-4">
                This stage has enough evidence for progression.
              </v-alert>
            </div>

            <!-- Path as journey map -->
            <div class="path-panel glass-card">
              <div class="path-panel__head">
                <div>
                  <h3 class="path-panel__title">Reading journey</h3>
                  <p class="path-panel__sub mb-0">{{ pathStages.length }} stages · follow the glow</p>
                </div>
                <div class="path-legend">
                  <span><i class="path-dot path-dot--current" /> Current</span>
                  <span><i class="path-dot path-dot--unlocked" /> Open</span>
                  <span><i class="path-dot path-dot--locked" /> Locked</span>
                </div>
              </div>

              <div class="path-map">
                <div v-for="level in cefrLevels" :key="level" class="path-row">
                  <div class="path-row__level">{{ level }}</div>
                  <div class="path-row__track">
                    <div
                      v-for="stage in stagesFor(level)"
                      :key="`${stage.cefr_level}-${stage.internal_stage}`"
                      class="stage-node"
                      :class="`stage-node--${stageStatus(stage)}`"
                      :title="stageReason(stage) || stageStatusLabel(stage)"
                    >
                      <div class="stage-node__orb">
                        <v-icon :icon="stageIcon(stage)" size="16" />
                      </div>
                      <div class="stage-node__meta">
                        <strong>{{ stage.internal_stage }}</strong>
                        <small>{{ stageStatusLabel(stage) }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <aside class="reading-side">
            <div class="side-stack glass-card">
              <div class="side-block">
                <div class="side-block__head">
                  <h3 class="side-block__title">Readiness</h3>
                  <v-chip :color="readinessColor" size="small" variant="tonal">{{ readinessStatusLabel }}</v-chip>
                </div>
                <p class="side-block__line mb-1">
                  <span>Target</span>
                  <strong>{{ readinessTargetText }}</strong>
                </p>
                <p class="side-block__hint mb-0">{{ readinessDetailText }}</p>
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
                  <v-progress-linear color="warning" height="8" rounded :model-value="retakeProgress" />
                </div>
              </div>

              <div class="side-block">
                <div class="side-block__head">
                  <h3 class="side-block__title">Recent</h3>
                  <v-chip size="small" color="primary" variant="tonal">{{ currentStageLabel }}</v-chip>
                </div>
                <div v-if="currentStageHistoryItems.length" class="history-list">
                  <div v-for="item in currentStageHistoryItems" :key="item.attempt_id" class="history-item">
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
                  No {{ currentStageLabel }} attempts yet. Start practice to build evidence for this stage.
                </v-alert>
                <div v-if="previousStageHistoryItems.length" class="previous-history mt-3 pt-3">
                  <v-btn
                    class="previous-history__toggle"
                    color="primary"
                    size="small"
                    variant="text"
                    :append-icon="showPreviousStageHistory ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                    @click="showPreviousStageHistory = !showPreviousStageHistory"
                  >
                    {{ previousStageHistoryLabel }}
                  </v-btn>
                  <div v-if="showPreviousStageHistory" class="history-list history-list--compact mt-2">
                    <div
                      v-for="item in previousStageHistoryItems"
                      :key="item.attempt_id"
                      class="history-item history-item--compact"
                    >
                      <div>
                        <div class="font-weight-medium">{{ labelize(item.mode) }} - {{ item.cefr_level }} {{ item.internal_stage }}</div>
                        <div class="text-caption text-medium-emphasis">{{ historyDateLabel(item) }}</div>
                      </div>
                      <v-chip size="x-small" :color="historyChipColor(item)" variant="tonal">
                        {{ historyStatusLabel(item) }}
                      </v-chip>
                    </div>
                  </div>
                </div>
              </div>

              <div class="side-block side-block--last">
                <h3 class="side-block__title mb-2">Snapshot</h3>
                <div v-if="summaryChips.length" class="d-flex flex-wrap gap-2">
                  <v-chip
                    v-for="chip in summaryChips"
                    :key="chip.label"
                    size="small"
                    variant="tonal"
                    :color="chip.color"
                  >
                    {{ chip.label }}: {{ chip.value }}
                  </v-chip>
                </div>
                <v-alert v-else type="info" variant="tonal" density="comfortable">
                  Evidence will appear after a few generated activities.
                </v-alert>
              </div>
            </div>
          </aside>
        </div>
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
          <v-chip v-if="grammarFocusLabel" class="mb-3" color="secondary" variant="tonal" size="small">
            Grammar: {{ grammarFocusLabel }}
          </v-chip>
          <h2 class="text-h5 font-weight-bold mb-4">{{ safeActivity.title }}</h2>
          <p class="reading-passage">{{ safeActivity.passage }}</p>
        </v-card>

        <v-card class="glass-card pa-6 reading-v2-text" variant="flat">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">Questions</h3>
          <div v-for="(question, index) in questions" :key="question.id" class="question-block">
            <div class="question-heading mb-3">
              <v-avatar class="question-number-badge" color="secondary" variant="tonal" size="30">{{ index + 1 }}</v-avatar>
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
              class="reading-true-false-toggle"
              color="secondary"
              variant="outlined"
              divided
              mandatory
            >
              <v-btn
                class="reading-true-false-choice"
                :class="{ 'reading-true-false-choice--selected': answers[question.id] === true }"
                :value="true"
              >
                True
              </v-btn>
              <v-btn
                class="reading-true-false-choice"
                :class="{ 'reading-true-false-choice--selected': answers[question.id] === false }"
                :value="false"
              >
                False
              </v-btn>
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
const SECRET_FIELDS = [
  'answer_key',
  'accepted_answers',
  'required_key_terms',
  'explanation',
  'evidence_quote',
  'feedback',
  'rationale',
  'expected_answer',
  'expected_answers',
  'correct_answer',
  'correct_answers',
  'correct_option',
  'correct_option_index',
  'correct_choice',
  'correct_choice_id',
  'correct',
  'is_correct',
  'rubric',
  'scoring',
  'scoring_metadata',
  'private_generation_metadata',
  'validation_metadata',
]
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
const showPreviousStageHistory = ref(false)

const cefrLevels = CEFR_LEVELS
const pathStages = computed(() => path.value?.stages || [])
const historyItems = computed(() =>
  (history.value?.attempts || []).filter((item) => isSubmittedHistoryItem(item)),
)
const currentStageLabel = computed(() =>
  `${overview.value?.current_cefr || 'A1'} ${overview.value?.current_stage || 'Beginner'}`,
)
const currentStageHistoryItems = computed(() =>
  historyItems.value.filter((item) => isCurrentStageHistoryItem(item)),
)
const previousStageHistoryItems = computed(() =>
  historyItems.value.filter((item) => !isCurrentStageHistoryItem(item)),
)
const previousStageHistoryLabel = computed(() => {
  const count = previousStageHistoryItems.value.length
  return `Previous stage history - ${count} ${count === 1 ? 'attempt' : 'attempts'}`
})
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
  const attemptsSubmitted = Number(evidence.attempts_submitted || 0)
  const uniqueActivities = Number(evidence.unique_generated_activities || 0)
  const answeredQuestions = Number(evidence.total_answered_questions || 0)
  const recentAverage = Number(evidence.recent_average_score || 0)
  const recentLowest = Number(evidence.recent_lowest_score || 0)
  const hasRecentWindow = (evidence.recent_attempt_ids || []).length >= 5
  return [
    {
      label: 'Practice attempts',
      value: `${attemptsSubmitted} / ${STAGE_REQUIREMENTS.attempts}`,
      met: attemptsSubmitted >= STAGE_REQUIREMENTS.attempts,
    },
    {
      label: 'Unique activities',
      value: `${uniqueActivities} / ${STAGE_REQUIREMENTS.uniqueActivities}`,
      met: uniqueActivities >= STAGE_REQUIREMENTS.uniqueActivities,
    },
    {
      label: 'Answered questions',
      value: `${answeredQuestions} / ${STAGE_REQUIREMENTS.questions}`,
      met: answeredQuestions >= STAGE_REQUIREMENTS.questions,
    },
    {
      label: 'Question types',
      value: `${questionTypes.length} / ${STAGE_REQUIREMENTS.questionTypes}${questionTypes.length ? ` (${questionTypes.map(questionTypeLabel).join(', ')})` : ''}`,
      met: questionTypes.length >= STAGE_REQUIREMENTS.questionTypes,
    },
    {
      label: 'Recent 5-attempt average',
      value: `${formatPercent(evidence.recent_average_score)} needed: ${STAGE_REQUIREMENTS.recentAverage}%`,
      met: hasRecentWindow && recentAverage >= STAGE_REQUIREMENTS.recentAverage,
    },
    {
      label: 'Recent low score check',
      value: hasRecentWindow
        ? recentLowest < STAGE_REQUIREMENTS.recentAttemptMinimum
          ? `One recent attempt is below ${STAGE_REQUIREMENTS.recentAttemptMinimum}%`
          : `No recent attempt below ${STAGE_REQUIREMENTS.recentAttemptMinimum}%`
        : 'Needs 5 recent attempts',
      met: hasRecentWindow && evidence.requirements?.no_recent_attempt_below_70 === true,
    },
  ]
})
const evidenceMetCount = computed(() => evidenceMetrics.value.filter((m) => m.met).length)
const evidenceTotalCount = computed(() => evidenceMetrics.value.length || 1)
const evidenceProgressPercent = computed(() =>
  Math.round((evidenceMetCount.value / Math.max(1, evidenceTotalCount.value)) * 100),
)
const weakestSubskills = computed(() => {
  const weak = currentStageEvidence.value?.weak_subskills
  if (Array.isArray(weak)) {
    return weak
      .map((item) => ({ ...item, name: item.name, score: Number(item.score_percent || 0) }))
      .filter((item) => item.name)
      .sort((a, b) => a.score - b.score)
  }
  const scores = currentStageEvidence.value?.core_subskill_scores || {}
  return Object.entries(scores)
    .map(([name, score]) => ({ name, score: Number(score || 0) }))
    .filter((item) => item.score < STAGE_REQUIREMENTS.coreSubskill)
    .sort((a, b) => a.score - b.score)
})
const underSampledSubskills = computed(() => {
  const underSampled = currentStageEvidence.value?.under_sampled_subskills
  if (!Array.isArray(underSampled)) return []
  return underSampled.filter((item) => item?.name)
})
const currentBlockingReasonTexts = computed(() =>
  (currentStageEvidence.value?.blocking_reasons || []).map((reason) =>
    friendlyReason(reason, {
      weakestSubskill: weakestSubskills.value[0]?.name,
      underSampledSubskill: underSampledSubskills.value[0]?.name,
    }),
  ),
)
const safeActivity = computed(() => stripSecrets(attempt.value?.activity || {}))
const questions = computed(() => (safeActivity.value?.questions || []).map(stripSecrets))
const grammarFocusLabel = computed(() =>
  safeActivity.value?.grammar_title || safeActivity.value?.grammar_id || '',
)
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
    return firstBlocker
      ? friendlyReason(firstBlocker, {
          weakestSubskill: weakestSubskills.value[0]?.name,
          underSampledSubskill: underSampledSubskills.value[0]?.name,
        })
      : ''
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
  const underSampledSubskill = context.underSampledSubskill ? `: ${labelize(context.underSampledSubskill)}` : ''
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
    each_core_subskill_has_min_evidence: underSampledSubskill
      ? `Complete more ${labelize(context.underSampledSubskill)} practice to confirm readiness.`
      : 'Complete more core subskill practice to confirm readiness.',
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
    each_tested_core_subskill_has_min_evidence: underSampledSubskill
      ? `Complete more ${labelize(context.underSampledSubskill)} practice to confirm readiness.`
      : 'Complete more core subskill practice to confirm readiness.',
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

function isCurrentStageHistoryItem(item) {
  return (
    item?.cefr_level === (overview.value?.current_cefr || 'A1')
    && item?.internal_stage === (overview.value?.current_stage || 'Beginner')
  )
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
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
  align-items: start;
}

.reading-overview {
  display: grid;
  gap: 18px;
}

/* —— Mission hero —— */
.mission-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1.25rem 1.5rem;
  align-items: center;
  padding: 1.35rem 1.5rem;
}

.mission-hero__glow {
  position: absolute;
  inset: -40% auto auto -10%;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(var(--v-theme-secondary), 0.22), transparent 68%);
  pointer-events: none;
}

.mission-hero__badge {
  position: relative;
  z-index: 1;
  width: 92px;
  height: 92px;
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(var(--v-theme-secondary), 0.28), rgba(var(--v-theme-primary), 0.12));
  border: 1px solid rgba(var(--v-theme-secondary), 0.35);
  box-shadow: 0 10px 28px -14px rgba(var(--v-theme-secondary), 0.55);
}

.mission-hero__cefr {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1;
  color: rgb(var(--v-theme-secondary));
}

.mission-hero__stage {
  margin-top: 4px;
  font-size: 0.65rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.mission-hero__copy {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.mission-hero__kicker {
  font-size: 0.72rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.mission-hero__title {
  font-size: 1.35rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}

.mission-hero__hint {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.mission-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem 1.25rem;
  margin-top: 0.85rem;
}

.mission-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.mission-stat__value {
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.mission-stat__label {
  font-size: 0.68rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mission-hero__actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  align-items: stretch;
}

/* —— Evidence panel —— */
.evidence-panel {
  padding: 1.2rem 1.25rem;
  margin-bottom: 1rem;
}

.evidence-panel__head {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.evidence-ring {
  --p: 0;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at center, rgba(var(--v-theme-surface), 0.95) 58%, transparent 59%),
    conic-gradient(
      rgb(var(--v-theme-secondary)) calc(var(--p) * 1%),
      rgba(var(--v-theme-on-surface), 0.12) 0
    );
  font-weight: 800;
  font-size: 0.85rem;
  color: rgb(var(--v-theme-secondary));
}

.evidence-panel__title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.2rem;
}

.evidence-panel__sub {
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.evidence-checklist {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
}

.evidence-check {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  column-gap: 0.55rem;
  row-gap: 0.1rem;
  align-items: start;
  text-align: left;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 12px;
  padding: 0.65rem 0.75rem;
  background: rgba(var(--v-theme-surface), 0.35);
  color: inherit;
}

.evidence-check--met {
  border-color: rgba(var(--v-theme-success), 0.28);
  background: rgba(var(--v-theme-success), 0.06);
}

.evidence-check .v-icon {
  grid-row: 1 / span 2;
  margin-top: 2px;
}

.evidence-check__label {
  font-size: 0.8rem;
  font-weight: 650;
  line-height: 1.25;
}

.evidence-check__value {
  font-size: 0.7rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
  line-height: 1.3;
}

.evidence-tags {
  display: grid;
  gap: 0.65rem;
  margin-top: 0.85rem;
}

.evidence-tags__group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
}

.evidence-tags__label {
  font-size: 0.7rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.45);
  margin-inline-end: 0.15rem;
}

/* —— Path journey —— */
.path-panel {
  padding: 1.2rem 1.25rem;
}

.path-panel__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.path-panel__title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.15rem;
}

.path-panel__sub {
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.path-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.72rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.path-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.path-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.path-dot--current {
  background: rgb(var(--v-theme-secondary));
  box-shadow: 0 0 0 3px rgba(var(--v-theme-secondary), 0.25);
}

.path-dot--unlocked {
  background: rgb(var(--v-theme-primary));
}

.path-dot--locked {
  background: rgba(var(--v-theme-on-surface), 0.28);
}

.path-map {
  display: grid;
  gap: 0.85rem;
  direction: ltr;
  text-align: left;
}

.path-row {
  display: grid;
  grid-template-columns: 44px 1fr;
  align-items: center;
  gap: 0.65rem;
}

.path-row__level {
  font-weight: 800;
  font-size: 0.95rem;
  color: rgb(var(--v-theme-secondary));
}

.path-row__track {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
  position: relative;
}

.stage-node {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 58px;
  padding: 0.55rem 0.65rem;
  border-radius: 14px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  background: rgba(var(--v-theme-surface), 0.45);
  direction: ltr;
  text-align: left;
}

.stage-node__orb {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.stage-node__meta {
  display: flex;
  flex-direction: column;
  gap: 0.05rem;
  min-width: 0;
}

.stage-node__meta strong {
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.2;
}

.stage-node__meta small {
  font-size: 0.65rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stage-node--current {
  border-color: rgba(var(--v-theme-secondary), 0.7);
  background: rgba(var(--v-theme-secondary), 0.14);
  box-shadow: 0 0 0 1px rgba(var(--v-theme-secondary), 0.2), 0 8px 22px -14px rgba(var(--v-theme-secondary), 0.55);
}

.stage-node--current .stage-node__orb {
  background: rgba(var(--v-theme-secondary), 0.22);
  color: rgb(var(--v-theme-secondary));
  animation: stage-pulse 2.2s ease-in-out infinite;
}

.stage-node--unlocked {
  border-color: rgba(var(--v-theme-primary), 0.4);
  background: rgba(var(--v-theme-primary), 0.08);
}

.stage-node--completed,
.stage-node--mastered {
  border-color: rgba(var(--v-theme-success), 0.45);
  background: rgba(var(--v-theme-success), 0.08);
}

.stage-node--locked {
  opacity: 0.58;
}

@keyframes stage-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(var(--v-theme-secondary), 0.35);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(var(--v-theme-secondary), 0);
  }
}

/* —— Side stack —— */
.side-stack {
  padding: 0;
  overflow: hidden;
}

.side-block {
  padding: 1rem 1.1rem;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.side-block--last {
  border-bottom: 0;
}

.side-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.side-block__title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}

.side-block__line {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.8125rem;
}

.side-block__line span {
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.side-block__hint {
  font-size: 0.78rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

.reason-list {
  margin: 0;
  padding-inline-start: 18px;
}

.history-list,
.result-list {
  display: grid;
  gap: 10px;
}

.history-list--compact {
  gap: 8px;
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

.history-item--compact {
  padding: 10px;
}

.previous-history {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.1);
}

.previous-history__toggle {
  padding-inline: 0;
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

.question-heading {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  direction: ltr;
  text-align: left;
}

.question-number-badge {
  flex: 0 0 auto;
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

.reading-true-false-toggle :deep(.v-btn) {
  color: rgb(var(--v-theme-secondary));
}

.reading-true-false-choice--selected {
  border-color: rgb(var(--v-theme-secondary)) !important;
  background-color: rgba(var(--v-theme-secondary), 0.16) !important;
  color: rgb(var(--v-theme-secondary)) !important;
  box-shadow:
    inset 0 0 0 999px rgba(var(--v-theme-secondary), 0.16),
    inset 0 0 0 1px rgba(var(--v-theme-secondary), 0.72) !important;
}

.reading-true-false-choice--selected :deep(.v-btn__overlay) {
  opacity: 0 !important;
}

.reading-true-false-toggle :deep(.v-btn.v-btn--active) {
  border-color: rgb(var(--v-theme-secondary));
  background-color: rgba(var(--v-theme-secondary), 0.16);
  color: rgb(var(--v-theme-secondary));
  box-shadow:
    inset 0 0 0 999px rgba(var(--v-theme-secondary), 0.16),
    inset 0 0 0 1px rgba(var(--v-theme-secondary), 0.72);
}

.reading-true-false-toggle :deep(.v-btn.v-btn--active .v-btn__overlay) {
  opacity: 0;
}

.reading-true-false-toggle :deep(.v-btn:focus-visible) {
  outline: 3px solid rgba(var(--v-theme-secondary), 0.35);
  outline-offset: 2px;
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

  .mission-hero {
    grid-template-columns: auto 1fr;
  }

  .mission-hero__actions {
    grid-column: 1 / -1;
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .mission-hero {
    grid-template-columns: 1fr;
    justify-items: start;
  }

  .evidence-checklist,
  .path-row__track {
    grid-template-columns: 1fr;
  }

  .path-row {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .stage-node--current .stage-node__orb {
    animation: none;
  }
}
</style>
