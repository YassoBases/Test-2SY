<template>
  <TeacherWorkspaceShell
    v-show="!reviewOpen"
    mode="page"
    class="teacher-quiz-results slide-up-enter-active"
  >
    <TeacherHero
      variant="compact"
      :eyebrow="$t('teacher.quizzes.resultsEyebrow')"
      :title="results?.quiz?.title || t('teacher.quizzes.resultsTitle')"
      :subtitle="classLabel"
    >
      <template #meta>
        <span class="teacher-quiz-results__meta-item">
          <v-icon size="14" class="me-1">mdi-clock-outline</v-icon>
          {{ $t('teacher.quizzes.lastUpdatedAt', { date: lastUpdatedLabel }) }}
        </span>
        <span class="teacher-quiz-results__meta-item">
          <v-icon size="14" class="me-1">mdi-account-group-outline</v-icon>
          {{ attemptsSummaryLabel }}
        </span>
      </template>

      <template #actions>
        <TeacherButtonGroup>
          <TeacherButton variant="tonal" :to="builderLink">
            {{ $t('teacher.actions.editQuiz') }}
          </TeacherButton>
          <TeacherButton variant="ghost" :to="{ name: 'teacher-quizzes' }">
            {{ $t('teacher.quizzes.allQuizzes') }}
          </TeacherButton>
        </TeacherButtonGroup>
      </template>
    </TeacherHero>

    <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">{{ error }}</v-alert>
    <v-progress-linear v-if="loading" indeterminate color="primary" />

    <template v-if="!loading">
      <TeacherSummaryGrid
        v-if="analytics"
        :columns="5"
        :aria-label="$t('teacher.quizzes.summaryAria')"
      >
        <TeacherStatCard
          compact
          :label="$t('teacher.quizzes.avgGrade')"
          :value="formatPercent(analytics.average_score)"
          value-dir="ltr"
        />
        <TeacherStatCard
          compact
          :label="$t('teacher.quizzes.highestGrade')"
          :value="formatPercent(analytics.highest_score)"
          value-dir="ltr"
        />
        <TeacherStatCard
          compact
          :label="$t('teacher.quizzes.lowestGrade')"
          :value="formatPercent(analytics.lowest_score)"
          value-dir="ltr"
        />
        <TeacherStatCard
          compact
          :label="$t('teacher.quizzes.completedAttempts')"
          :value="completedAttemptsCount"
          :subtitle="completionSubtitle"
          value-dir="ltr"
        />
        <TeacherStatCard
          compact
          :label="$t('teacher.status.pendingGrading')"
          :value="pendingGradingCount"
          :subtitle="pendingGradingSubtitle"
          value-dir="ltr"
        />
      </TeacherSummaryGrid>

      <TeacherWorkspaceCard
        v-if="insights.length"
        :title="$t('teacher.quizzes.insightsTitle')"
        :meta="$t('teacher.quizzes.insightsMeta')"
        :aria-label="$t('teacher.quizzes.insightsAria')"
      >
        <div class="teacher-quiz-results__insights">
          <TeacherWarningCard
            v-for="(insight, index) in insights"
            :key="index"
            :variant="insight.variant"
            :title="insight.title"
            :message="insight.message"
          />
        </div>
      </TeacherWorkspaceCard>

      <TeacherWorkspaceCard
        :title="$t('teacher.quizzes.studentResults')"
        :meta="resultsMeta"
        :aria-label="$t('teacher.quizzes.resultsTableAria')"
      >
        <TeacherEmptyStateCard
          v-if="results && !results.attempts.length"
          icon="mdi-clipboard-text-outline"
          :title="$t('teacher.quizzes.noAttempts')"
          :description="$t('teacher.quizzes.noAttemptsHint')"
        />

        <TeacherTable v-else-if="results?.attempts.length">
          <thead>
            <tr>
              <th>{{ $t('teacher.labels.student') }}</th>
              <th>{{ $t('teacher.labels.status') }}</th>
              <th>{{ $t('teacher.labels.score') }}</th>
              <th>{{ $t('teacher.labels.percent') }}</th>
              <th>{{ $t('teacher.quizzes.submission') }}</th>
              <th class="text-end">{{ $t('teacher.labels.action') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="attempt in results.attempts" :key="attempt.id">
              <td>
                <span class="tds-table__cell-strong">{{ attempt.student_name }}</span>
              </td>
              <td>
                <span class="tds-table__cell-strong">{{ statusLabel(attempt.status) }}</span>
                <span
                  v-if="attempt.pending_essay_count"
                  class="tds-table__cell-muted"
                >
                  · {{ $t('teacher.labels.essayCount', { count: attempt.pending_essay_count }) }}
                </span>
              </td>
              <td>
                <span class="tds-table__cell-strong" dir="ltr">
                  {{ formatScore(attempt.score, attempt.max_score) }}
                </span>
              </td>
              <td dir="ltr">{{ formatPercent(attempt.percent) }}</td>
              <td class="tds-table__cell-muted">{{ formatDate(attempt.submitted_at) }}</td>
              <td class="text-end">
                <TeacherButton
                  size="small"
                  variant="tonal"
                  :disabled="attempt.status === 'in_progress'"
                  @click="openAttempt(attempt.id)"
                >
                  {{ $t('teacher.actions.review') }}
                </TeacherButton>
              </td>
            </tr>
          </tbody>
        </TeacherTable>
      </TeacherWorkspaceCard>
    </template>
  </TeacherWorkspaceShell>

  <Teleport to="body">
    <TeacherWorkspaceShell
      v-if="reviewOpen && attemptDetail"
      mode="fullscreen"
    >
      <template #header>
        <TeacherHero
          class="tds-workspace-shell__hero"
          variant="compact"
          :eyebrow="results?.quiz?.title"
          :title="attemptDetail.student_name"
        />
      </template>

      <template #header-actions>
        <TeacherButton variant="ghost" @click="closeReview">
          <v-icon start size="18">mdi-close</v-icon>
          {{ $t('common.close') }}
        </TeacherButton>
      </template>

      <TeacherWorkspaceCard :title="$t('teacher.quizzes.attemptSummary')">
        <TeacherSummaryGrid :columns="3" :aria-label="$t('teacher.quizzes.attemptSummary')">
          <TeacherStatCard
            compact
            :label="$t('teacher.labels.score')"
            :value="formatScore(attemptDetail.score, attemptDetail.max_score)"
            value-dir="ltr"
          />
          <TeacherStatCard
            compact
            :label="$t('teacher.labels.percent')"
            :value="formatPercent(attemptDetail.percent)"
            value-dir="ltr"
          />
          <TeacherStatCard
            compact
            :label="$t('teacher.labels.status')"
            :value="statusLabel(attemptDetail.status)"
          />
        </TeacherSummaryGrid>
      </TeacherWorkspaceCard>

      <TeacherWorkspaceCard
        v-for="ans in attemptDetail.answers"
        :key="ans.question_id"
        :title="typeLabel(ans.question_type)"
        :meta="$t('teacher.labels.pointsCount', { count: formatScore(ans.points_earned ?? 0, ans.max_points) })"
      >
        <p class="teacher-quiz-results__question-text">{{ ans.question_text }}</p>

        <div class="teacher-quiz-results__answer-box">
          <p class="tds-table__cell-muted mb-1">{{ $t('teacher.labels.studentAnswer') }}</p>
          <p class="mb-0">{{ formatAnswer(ans.answer) }}</p>
        </div>

        <template v-if="ans.requires_manual_grading && ans.pending_grading">
          <v-text-field
            v-model.number="essayGrades[ans.question_id].points"
            type="number"
            :max="ans.max_points"
            min="0"
            :label="$t('teacher.labels.points')"
            variant="outlined"
            density="comfortable"
            class="mt-4 mb-3"
          />
          <v-textarea
            v-model="essayGrades[ans.question_id].feedback"
            :label="$t('teacher.labels.teacherNotes')"
            rows="3"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <TeacherButton
            size="small"
            variant="primary"
            :loading="gradingId === ans.question_id"
            @click="submitGrade(ans.question_id)"
          >
            {{ $t('teacher.actions.saveGrading') }}
          </TeacherButton>
        </template>
        <TeacherWarningCard
          v-else-if="ans.teacher_feedback"
          variant="info"
          :title="$t('teacher.labels.teacherNotes')"
          :message="ans.teacher_feedback"
        />
      </TeacherWorkspaceCard>
    </TeacherWorkspaceShell>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute } from 'vue-router'
import { fetchTeacherCourses } from '../../api/teacherCourses.js'
import {
  fetchManualQuizAttempt,
  fetchManualQuizResults,
  fetchManualQuizAnalytics,
  gradeManualEssay,
} from '../../api/manualQuizzes.js'
import { getErrorMessage } from '../../api/client.js'
import { formatLastSeen } from '../../utils/sessionDisplay.js'
import {
  TeacherWorkspaceShell,
  TeacherHero,
  TeacherStatCard,
  TeacherSummaryGrid,
  TeacherWorkspaceCard,
  TeacherTable,
  TeacherButton,
  TeacherButtonGroup,
  TeacherEmptyStateCard,
  TeacherWarningCard,
} from '../../components/teacher/design-system/index.js'

const route = useRoute()
const courseId = computed(() => Number(route.params.courseId))
const quizId = computed(() => Number(route.params.quizId))

const loading = ref(true)
const error = ref('')
const results = ref(null)
const analytics = ref(null)
const courseInfo = ref(null)
const reviewOpen = ref(false)
const attemptDetail = ref(null)
const essayGrades = reactive({})
const gradingId = ref(null)

const builderLink = computed(() => ({
  name: 'teacher-quiz-builder',
  params: { courseId: courseId.value, quizId: quizId.value },
}))

const classLabel = computed(() => {
  const subject = courseInfo.value?.subject_name || courseInfo.value?.title
  const grade = courseInfo.value?.grade
  if (subject && grade) return t('teacher.analytics.classLabel', { subject, grade })
  if (subject) return subject
  return t('teacher.quizzes.teachingSpace')
})

const lastUpdatedLabel = computed(() => {
  const attempts = results.value?.attempts || []
  const latest = [...attempts]
    .filter((a) => a.submitted_at)
    .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]
  if (latest?.submitted_at) return formatLastSeen(latest.submitted_at)
  if (results.value?.quiz?.created_at) return formatLastSeen(results.value.quiz.created_at)
  return '—'
})

const attemptsSummaryLabel = computed(() => {
  const total = results.value?.attempts?.length ?? 0
  const completed = completedAttemptsCount.value
  if (!total) return t('teacher.quizzes.noAttemptsShort')
  if (completed === total) return t('teacher.quizzes.attemptsTotal', { count: total })
  return t('teacher.quizzes.attemptsCompleted', { completed, total })
})

const completedAttemptsCount = computed(() => {
  const attempts = results.value?.attempts || []
  return attempts.filter((a) => a.status !== 'in_progress').length
})

const pendingGradingCount = computed(() =>
  (results.value?.attempts || []).reduce((sum, a) => sum + (a.pending_essay_count || 0), 0),
)

const completionSubtitle = computed(() => {
  if (!analytics.value?.enrolled_students) return undefined
  return t('teacher.quizzes.enrolledPercent', { percent: analytics.value.completion_rate ?? 0 })
})

const pendingGradingSubtitle = computed(() => {
  if (!pendingGradingCount.value) return t('teacher.quizzes.noPendingGrading')
  return t('teacher.quizzes.essayQuestions')
})

const resultsMeta = computed(() => {
  const total = results.value?.quiz?.total_points
  const points = total != null ? t('teacher.labels.pointsCount', { count: total }) : '—'
  const count = results.value?.attempts?.length ?? 0
  return t('teacher.quizzes.totalScoreAttempts', { points, count })
})

const insights = computed(() => {
  const items = []
  const attempts = results.value?.attempts || []
  const passing = Number(results.value?.quiz?.passing_score_percent ?? 60)
  const pending = pendingGradingCount.value

  if (pending > 0) {
    items.push({
      variant: 'warning',
      title: t('teacher.quizzes.essaysPending'),
      message: t('teacher.quizzes.essayReviewHint', { count: pending }),
    })
  }

  const belowPassing = attempts.filter(
    (a) => a.status !== 'in_progress' && a.percent != null && Number(a.percent) < passing,
  )
  if (belowPassing.length > 0) {
    items.push({
      variant: 'warning',
      title: t('teacher.quizzes.belowPassing'),
      message: t('teacher.quizzes.belowPassingHint', { count: belowPassing.length, threshold: passing }),
    })
  }

  const inProgress = attempts.filter((a) => a.status === 'in_progress').length
  if (inProgress > 0) {
    items.push({
      variant: 'info',
      title: t('teacher.quizzes.inProgressAttempts'),
      message: t('teacher.quizzes.inProgressHint', { count: inProgress }),
    })
  }

  if (
    analytics.value?.enrolled_students > 0
    && analytics.value.completion_rate < 50
    && completedAttemptsCount.value > 0
  ) {
    items.push({
      variant: 'info',
      title: t('teacher.quizzes.lowCompletion'),
      message: t('teacher.quizzes.lowCompletionHint', { percent: analytics.value.completion_rate, count: `${analytics.value.attempted_count} / ${analytics.value.enrolled_students}` }),
    })
  }

  const highest = analytics.value?.highest_score
  const lowest = analytics.value?.lowest_score
  if (highest != null && lowest != null && highest - lowest >= 30) {
    items.push({
      variant: 'info',
      title: t('teacher.quizzes.highVariance'),
      message: t('teacher.quizzes.varianceHint', { high: formatPercent(highest), low: formatPercent(lowest) }),
    })
  }

  if (!attempts.length) {
    items.push({
      variant: 'info',
      title: t('teacher.quizzes.noAttempts'),
      message: t('teacher.quizzes.shareHint'),
    })
  }

  return items
})

function statusLabel(status) {
  const map = { in_progress: t('teacher.status.inProgress'), submitted: t('teacher.status.submitted'), graded: t('teacher.status.graded') }
  return map[status] || status
}

function typeLabel(questionType) {
  const key = `teacher.quizzes.types.${questionType}`
  const label = t(key)
  return label !== key ? label : questionType
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ar-SY', { dateStyle: 'medium', timeStyle: 'short' })
}

function formatScore(score, maxScore) {
  const s = Number(score)
  const m = Number(maxScore)
  if (!Number.isFinite(s) || !Number.isFinite(m)) return '—'
  const displayScore = Number.isInteger(s) ? s : s.toFixed(1)
  const displayMax = Number.isInteger(m) ? m : m.toFixed(1)
  return `${displayScore} / ${displayMax}`
}

function formatPercent(value) {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  return `${n % 1 === 0 ? n : n.toFixed(1)}%`
}

function formatAnswer(answer) {
  if (answer == null) return '—'
  if (typeof answer === 'object') {
    if ('text' in answer) return answer.text || '—'
    if ('selected_index' in answer) return t('teacher.labels.optionNumber', { n: Number(answer.selected_index) + 1 })
    if ('value' in answer) return answer.value ? t('teacher.labels.trueLabel') : t('teacher.labels.falseLabel')
  }
  return String(answer)
}

async function loadCourseInfo() {
  try {
    const list = await fetchTeacherCourses()
    courseInfo.value = list.find((c) => Number(c.id) === courseId.value) || null
  } catch {
    courseInfo.value = null
  }
}

async function openAttempt(attemptId) {
  try {
    attemptDetail.value = await fetchManualQuizAttempt(courseId.value, quizId.value, attemptId)
    for (const ans of attemptDetail.value.answers) {
      if (ans.requires_manual_grading) {
        essayGrades[ans.question_id] = {
          points: ans.points_earned ?? 0,
          feedback: ans.teacher_feedback || '',
        }
      }
    }
    reviewOpen.value = true
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadAttempt'))
  }
}

function closeReview() {
  reviewOpen.value = false
  attemptDetail.value = null
}

async function submitGrade(questionId) {
  gradingId.value = questionId
  try {
    const g = essayGrades[questionId]
    attemptDetail.value = await gradeManualEssay(
      courseId.value,
      quizId.value,
      attemptDetail.value.id,
      questionId,
      { points_earned: g.points, teacher_feedback: g.feedback, publish: true },
    )
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveGrading'))
  } finally {
    gradingId.value = null
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [resultsData, analyticsData] = await Promise.all([
      fetchManualQuizResults(courseId.value, quizId.value),
      fetchManualQuizAnalytics(courseId.value, quizId.value),
    ])
    results.value = resultsData
    analytics.value = analyticsData
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadResults'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadCourseInfo()])
})

onUnmounted(() => {
  document.body.style.overflow = ''
})

watch(reviewOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})
</script>

<style scoped>
.teacher-quiz-results__meta-item {
  display: inline-flex;
  align-items: center;
  font-size: var(--em-text-sm);
  font-weight: 500;
  color: var(--em-text-muted);
}

.teacher-quiz-results__insights {
  display: flex;
  flex-direction: column;
  gap: var(--em-space-sm);
}

.teacher-quiz-results__question-text {
  margin: 0 0 var(--em-space-md);
  font-size: var(--em-text-body);
  font-weight: 600;
  line-height: 1.55;
  color: var(--em-text);
}

.teacher-quiz-results__answer-box {
  padding: 12px 14px;
  border-radius: var(--em-radius-sm);
  border: 1px solid var(--em-border-subtle);
  background: var(--em-surface-control);
}
</style>
