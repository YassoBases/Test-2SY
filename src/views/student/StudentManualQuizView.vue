<template>
  <div class="slide-up-enter-active quiz-take" dir="rtl">
    <PageHeader
      :eyebrow="t('student.manualQuiz.header.eyebrow')"
      :title="take?.quiz?.title || t('student.manualQuiz.defaultTitle')"
      :subtitle="subtitle"
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

    <v-card v-if="result" class="quiz-panel pa-8 mb-5 text-center" variant="flat">
      <v-icon size="64" :color="result.passed ? 'success' : 'warning'" class="mb-3">
        {{ result.passed ? 'mdi-check-circle' : 'mdi-alert-circle' }}
      </v-icon>
      <h2 class="text-h4 font-weight-bold mb-2">
        {{ result.score }} / {{ result.max_score }}
      </h2>
      <p class="text-h6 text-medium-emphasis mb-1">
        {{ result.percent != null ? `${result.percent}%` : t('student.manualQuiz.pendingGrading') }}
      </p>
      <p class="text-body-2 text-medium-emphasis mb-4">
        <span v-if="result.passed === true">{{ t('student.manualQuiz.passed') }}</span>
        <span v-else-if="result.passed === false">{{ t('student.manualQuiz.failed') }}</span>
        <span v-else-if="hasPendingEssays">{{ t('student.manualQuiz.pendingEssays') }}</span>
        {{ t('student.manualQuiz.passingScore', { pct: take?.quiz?.passing_score_percent ?? '—' }) }}
      </p>
      <v-btn variant="tonal" :to="courseLink">{{ t('student.manualQuiz.backToCourse') }}</v-btn>
    </v-card>

    <template v-else-if="take && !loading">
      <v-alert
        v-if="timeRemaining != null"
        :type="timeRemaining <= 60 ? 'warning' : 'info'"
        variant="tonal"
        density="comfortable"
        class="mb-4 rounded-lg"
      >
        <div class="d-flex align-center justify-space-between flex-wrap gap-2">
          <span>{{ t('student.manualQuiz.timer.remainingLine', { time: formatTime(timeRemaining) }) }}</span>
          <span v-if="timeRemaining <= 0" class="text-error">{{ t('student.manualQuiz.timer.expired') }}</span>
        </div>
      </v-alert>

      <v-card v-if="!take.attempt_id && !started" class="quiz-panel pa-8 text-center mb-5" variant="flat">
        <p class="text-body-1 mb-2">{{ t('student.manualQuiz.questionsCount', { n: take.quiz.question_count }) }}</p>
        <p class="text-body-2 font-weight-medium mb-2">
          {{ t('student.manualQuiz.totalPoints', { n: totalPoints }) }}
        </p>
        <p v-if="take.quiz.duration_minutes" class="text-caption text-medium-emphasis mb-2">
          {{ t('student.manualQuiz.duration', { n: take.quiz.duration_minutes }) }}
        </p>
        <p class="text-caption text-medium-emphasis mb-4">
          {{ t('student.manualQuiz.passingScore', { pct: take.quiz.passing_score_percent }) }}
        </p>
        <v-btn size="large" class="btn-glow" :loading="starting" @click="begin">{{ t('student.manualQuiz.startCta') }}</v-btn>
      </v-card>

      <template v-else-if="take.attempt_id">
        <v-card class="quiz-panel pa-5 mb-4" variant="flat">
          <div class="d-flex justify-space-between align-center flex-wrap gap-2 mb-3">
            <div class="text-caption text-medium-emphasis">
              {{ t('student.manualQuiz.questionProgress', { current: currentIndex + 1, total: take.questions.length }) }}
            </div>
            <v-chip size="small" variant="tonal">{{ t('student.manualQuiz.points', { n: currentQuestion.points }) }}</v-chip>
          </div>
          <p class="text-body-1 font-weight-medium mb-4">{{ currentQuestion.question_text }}</p>

          <template v-if="currentQuestion.question_type === 'multiple_choice'">
            <v-radio-group v-model="answers[currentQuestion.id]" @update:model-value="persistAnswer">
              <v-radio
                v-for="(opt, i) in currentQuestion.options"
                :key="i"
                :label="opt"
                :value="{ selected_index: i }"
              />
            </v-radio-group>
          </template>

          <template v-else-if="currentQuestion.question_type === 'true_false'">
            <v-radio-group v-model="answers[currentQuestion.id]" @update:model-value="persistAnswer">
              <v-radio :label="t('student.manualQuiz.true')" :value="{ value: true }" />
              <v-radio :label="t('student.manualQuiz.false')" :value="{ value: false }" />
            </v-radio-group>
          </template>

          <template v-else-if="currentQuestion.question_type === 'short_answer'">
            <v-text-field
              v-model="shortTexts[currentQuestion.id]"
              :label="t('student.manualQuiz.yourAnswer')"
              variant="outlined"
              @blur="saveShort"
            />
          </template>

          <template v-else-if="currentQuestion.question_type === 'essay'">
            <v-textarea
              v-model="essayTexts[currentQuestion.id]"
              :label="t('student.manualQuiz.essayAnswer')"
              rows="5"
              variant="outlined"
              @blur="saveEssay"
            />
            <p class="text-caption text-warning mt-1">{{ t('student.manualQuiz.essayGradingNote') }}</p>
          </template>
        </v-card>

        <div class="d-flex justify-space-between gap-2">
          <v-btn variant="tonal" :disabled="currentIndex === 0" @click="currentIndex--">{{ t('student.manualQuiz.previous') }}</v-btn>
          <v-btn
            v-if="currentIndex < take.questions.length - 1"
            color="primary"
            @click="currentIndex++"
          >
            {{ t('student.manualQuiz.next') }}
          </v-btn>
          <v-btn v-else color="success" :loading="submitting" @click="submit">{{ t('student.manualQuiz.submitCta') }}</v-btn>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import {
  fetchManualQuizTake,
  saveManualQuizAnswers,
  startManualQuiz,
  submitManualQuiz,
} from '../../api/manualQuizzes.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()
const route = useRoute()
const quizId = computed(() => Number(route.params.quizId))
const courseId = computed(() => Number(route.query.courseId))

const loading = ref(true)
const starting = ref(false)
const submitting = ref(false)
const started = ref(false)
const error = ref('')
const take = ref(null)
const result = ref(null)
const currentIndex = ref(0)
const timeRemaining = ref(null)
const answers = reactive({})
const shortTexts = reactive({})
const essayTexts = reactive({})

let timerHandle = null
let autoSubmitting = false

const currentQuestion = computed(() => take.value?.questions?.[currentIndex.value])
const hasPendingEssays = computed(() =>
  result.value?.answers?.some((a) => a.pending_grading),
)
const courseLink = computed(() => ROUTES.STUDENT_COURSE(courseId.value))
const totalPoints = computed(() =>
  take.value?.quiz?.total_points ??
  take.value?.questions?.reduce((sum, q) => sum + Number(q.points || 0), 0) ??
  0,
)
const subtitle = computed(() => {
  if (result.value) return t('student.manualQuiz.subtitle.result')
  return take.value?.quiz?.description || t('student.manualQuiz.subtitle.default')
})

function formatTime(sec) {
  const safe = Math.max(0, Number(sec) || 0)
  const m = Math.floor(safe / 60)
  const s = safe % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

function clearTimer() {
  if (timerHandle) {
    clearInterval(timerHandle)
    timerHandle = null
  }
}

function startCountdown(seconds) {
  clearTimer()
  if (seconds == null) {
    timeRemaining.value = null
    return
  }
  timeRemaining.value = Math.max(0, Number(seconds) || 0)
  timerHandle = setInterval(() => {
    if (timeRemaining.value == null) return
    if (timeRemaining.value <= 0) {
      clearTimer()
      if (!autoSubmitting && !result.value && take.value?.attempt_id) {
        autoSubmitting = true
        submit(true)
      }
      return
    }
    timeRemaining.value -= 1
  }, 1000)
}

async function syncTimeFromServer() {
  if (!take.value?.attempt_id || result.value) return
  try {
    const fresh = await fetchManualQuizTake(quizId.value)
    take.value = { ...take.value, ...fresh, answers: take.value.answers }
    if (fresh.time_remaining_seconds != null) {
      startCountdown(fresh.time_remaining_seconds)
    }
  } catch {
    /* ignore background sync errors */
  }
}

function initAnswersFromTake() {
  const data = take.value
  if (!data) return
  for (const [qid, val] of Object.entries(data.answers || {})) {
    const id = Number(qid)
    answers[id] = val
    if (val?.text != null) {
      if (data.questions.find((q) => q.id === id)?.question_type === 'essay') {
        essayTexts[id] = val.text
      } else {
        shortTexts[id] = val.text
      }
    }
  }
}

async function persistAnswer() {
  if (!take.value?.attempt_id || !currentQuestion.value) return
  const qid = currentQuestion.value.id
  await saveOne(qid, answers[qid])
}

async function saveShort() {
  const qid = currentQuestion.value.id
  answers[qid] = { text: shortTexts[qid] }
  await saveOne(qid, answers[qid])
}

async function saveEssay() {
  const qid = currentQuestion.value.id
  answers[qid] = { text: essayTexts[qid] }
  await saveOne(qid, answers[qid])
}

async function saveOne(questionId, answer) {
  try {
    await saveManualQuizAnswers(take.value.attempt_id, [{ question_id: questionId, answer }])
  } catch (e) {
    if (e.response?.status === 400) {
      error.value = getErrorMessage(e, t('student.manualQuiz.errors.timeExpired'))
      clearTimer()
    }
  }
}

async function begin() {
  starting.value = true
  error.value = ''
  try {
    take.value = await startManualQuiz(quizId.value)
    started.value = true
    initAnswersFromTake()
    startCountdown(take.value.time_remaining_seconds)
  } catch (e) {
    error.value = getErrorMessage(e, t('student.manualQuiz.errors.start'))
  } finally {
    starting.value = false
  }
}

async function submit(fromTimer = false) {
  if (submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const batch = take.value.questions.map((q) => {
      let answer = answers[q.id]
      if (q.question_type === 'short_answer') answer = { text: shortTexts[q.id] || '' }
      if (q.question_type === 'essay') answer = { text: essayTexts[q.id] || '' }
      return { question_id: q.id, answer: answer ?? null }
    })
    if (take.value.attempt_id) {
      try {
        await saveManualQuizAnswers(take.value.attempt_id, batch)
      } catch (e) {
        if (!fromTimer) throw e
      }
    }
    result.value = await submitManualQuiz(take.value.attempt_id)
    clearTimer()
    timeRemaining.value = null
  } catch (e) {
    error.value = getErrorMessage(e, t('student.manualQuiz.errors.submit'))
    autoSubmitting = false
  } finally {
    submitting.value = false
  }
}

function onVisibilityChange() {
  if (document.visibilityState === 'visible') {
    syncTimeFromServer()
  }
}

onMounted(async () => {
  document.addEventListener('visibilitychange', onVisibilityChange)
  try {
    take.value = await fetchManualQuizTake(quizId.value)
    initAnswersFromTake()
    if (
      take.value.attempt_id &&
      (take.value.quiz?.attempt_status === 'graded' || take.value.quiz?.attempt_status === 'submitted')
    ) {
      const { fetchManualQuizAttemptResult } = await import('../../api/manualQuizzes.js')
      result.value = await fetchManualQuizAttemptResult(take.value.attempt_id)
      started.value = true
    } else if (take.value.attempt_id) {
      started.value = true
      startCountdown(take.value.time_remaining_seconds)
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('student.manualQuiz.errors.load'))
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  clearTimer()
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.quiz-panel {
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), 0.12);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
</style>
