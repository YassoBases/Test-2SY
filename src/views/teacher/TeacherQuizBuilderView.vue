<template>
  <div class="slide-up-enter-active teacher-quiz-detail quiz-builder" dir="rtl">
    <v-alert v-if="error && !questionEditorOpen" type="error" variant="tonal" class="mb-3 rounded-lg">
      {{ error }}
    </v-alert>
    <v-alert v-if="saved && !questionEditorOpen" type="success" variant="tonal" class="mb-3 rounded-lg">
      {{ $t('teacher.status.saved') }}
    </v-alert>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-3" />

    <template v-if="!loading">
      <div v-show="!questionEditorOpen">
        <TeacherQuizDetailHero
          :title="heroTitle"
          :updated-label="isNew ? '' : updatedLabel"
          :is-published="quiz.is_published"
          :needs-review="needsReview"
          :show-actions="!isNew"
          :publish-loading="publishToggling"
          @edit="scrollToForm"
          @preview="previewOpen = true"
          @toggle-publish="togglePublish"
        />

        <TeacherQuizClassContext
          :subject="courseSubject"
          :grade="courseGrade"
        />

        <TeacherQuizSettingsCard
          v-model:title="quiz.title"
          v-model:description="quiz.description"
          v-model:duration-minutes="quiz.duration_minutes"
          v-model:passing-score="quiz.passing_score_percent"
          v-model:due-at-local="dueAtLocal"
          v-model:is-published="quiz.is_published"
          :due-at-min="dueAtMin"
          :due-at-error="dueAtError"
          :total-points="totalPoints"
          :saving="saving"
          @save="saveQuiz"
          @update:due-at-local="validateDueAt"
        />

        <TeacherQuizKpiStrip v-if="!isNew" :items="detailKpiItems" />

        <section v-if="!isNew" class="teacher-quiz-detail__section" aria-labelledby="quiz-questions-title">
          <div class="teacher-quiz-detail__section-head">
            <div>
              <h2 id="quiz-questions-title" class="teacher-quiz-detail__section-title">{{ $t('teacher.labels.questions') }}</h2>
              <p class="teacher-quiz-detail__section-sub">
                {{ $t('teacher.quizzes.questionsPointsSummary', { questions: questions.length, points: totalPoints }) }}
              </p>
            </div>
            <v-btn color="secondary" variant="flat" size="small" rounded="lg" @click="openAddQuestion">
              <v-icon start size="16">mdi-plus</v-icon>
              {{ $t('teacher.actions.addQuestion') }}
            </v-btn>
          </div>

          <div v-if="questions.length" class="teacher-quiz-detail__questions">
            <TeacherQuizQuestionCard
              v-for="(q, idx) in questions"
              :key="q.id"
              :question="q"
              :index="idx + 1"
              @open="openEditQuestion(q)"
              @edit="openEditQuestion(q)"
              @delete="removeQuestion(q.id)"
            />
          </div>

          <div v-else class="teacher-quiz-detail__empty">
            <span class="teacher-quiz-detail__empty-icon" aria-hidden="true">
              <v-icon size="28">mdi-help-circle-outline</v-icon>
            </span>
            <h3 class="teacher-quiz-detail__empty-title">{{ $t('teacher.quizzes.noQuestionsYet') }}</h3>
            <p class="teacher-quiz-detail__empty-desc">{{ $t('teacher.quizzes.addBeforePublish') }}</p>
            <v-btn class="btn-glow" rounded="lg" @click="openAddQuestion">
              <v-icon start>mdi-plus</v-icon>
              {{ $t('teacher.actions.addQuestion') }}
            </v-btn>
          </div>
        </section>

        <TeacherQuizResultsSummary
          v-if="!isNew && quiz.id"
          :analytics="analytics"
          :attempts="resultsData?.attempts || []"
          :course-id="courseId"
          :quiz-id="quiz.id"
        />

        <div class="teacher-quiz-detail__back">
          <v-btn variant="text" rounded="lg" :to="{ name: 'teacher-quizzes' }">
            <v-icon start>mdi-arrow-right</v-icon>
            {{ $t('teacher.actions.backToQuizzes') }}
          </v-btn>
        </div>

        <TeacherQuizPreviewDialog
          v-model:open="previewOpen"
          :title="quiz.title"
          :description="quiz.description"
          :duration-minutes="quiz.duration_minutes"
          :passing-score="quiz.passing_score_percent"
          :questions="questions"
        />
      </div>

      <!-- Full-screen question editor -->
      <Teleport to="body">
        <TeacherQuizQuestionEditor
          v-if="questionEditorOpen"
          :quiz-title="quiz.title || t('teacher.quizzes.newQuiz')"
          :editing-question-id="editingQuestionId"
          :question-form="questionForm"
          :question-form-error="questionFormError"
          :saving-question="savingQuestion"
          :correct-answer-items="correctAnswerItems"
          :editor-menu-props="editorMenuProps"
          @close="closeQuestionEditor"
          @save="saveQuestion"
          @set-question-type="setQuestionType"
        />
      </Teleport>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute, useRouter, isNavigationFailure } from 'vue-router'
import TeacherQuizClassContext from '../../components/teacher/quizzes/TeacherQuizClassContext.vue'
import TeacherQuizDetailHero from '../../components/teacher/quizzes/TeacherQuizDetailHero.vue'
import TeacherQuizKpiStrip from '../../components/teacher/quizzes/TeacherQuizKpiStrip.vue'
import TeacherQuizQuestionCard from '../../components/teacher/quizzes/TeacherQuizQuestionCard.vue'
import TeacherQuizResultsSummary from '../../components/teacher/quizzes/TeacherQuizResultsSummary.vue'
import TeacherQuizSettingsCard from '../../components/teacher/quizzes/TeacherQuizSettingsCard.vue'
import TeacherQuizPreviewDialog from '../../components/teacher/quizzes/TeacherQuizPreviewDialog.vue'
import TeacherQuizQuestionEditor from '../../components/teacher/quizzes/TeacherQuizQuestionEditor.vue'
import {
  addManualQuestion,
  createManualQuiz,
  deleteManualQuestion,
  fetchManualQuizAnalytics,
  fetchManualQuizDetail,
  fetchManualQuizResults,
  updateManualQuestion,
  updateManualQuiz,
} from '../../api/manualQuizzes.js'
import { fetchTeacherCourses } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { formatLastSeen } from '../../utils/sessionDisplay.js'
import '../../assets/styles/teacher-quiz-detail.css'
import '../../assets/styles/teacher-quizzes.css'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => Number(route.params.courseId))
const quizIdParam = computed(() => route.params.quizId)
const isNew = computed(() => quizIdParam.value === 'new')

const loading = ref(true)
const saving = ref(false)
const savingQuestion = ref(false)
const error = ref('')
const saved = ref(false)
const dueAtError = ref('')
const questionFormError = ref('')
const questionEditorOpen = ref(false)
const editingQuestionId = ref(null)
const previewOpen = ref(false)
const publishToggling = ref(false)
const courseInfo = ref(null)
const analytics = ref(null)
const resultsData = ref(null)

const quiz = reactive({
  id: null,
  title: '',
  description: '',
  duration_minutes: null,
  passing_score_percent: 60,
  is_published: false,
  due_at: null,
  total_points: 0,
  attempt_count: 0,
  created_at: null,
})

const questions = ref([])
const dueAtLocal = ref('')

const questionForm = reactive({
  question_type: 'multiple_choice',
  question_text: '',
  options: ['', '', '', ''],
  correct_index: 0,
  correct_bool: true,
  correct_text: '',
  points: 1,
})

const totalPoints = computed(() =>
  questions.value.reduce((sum, q) => sum + Number(q.points || 0), 0),
)

const dueAtMin = computed(() => {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
})

const heroTitle = computed(() => quiz.title?.trim() || (isNew.value ? t('teacher.quizzes.newQuiz') : t('teacher.labels.quiz')))

const courseSubject = computed(
  () => courseInfo.value?.subject_name || courseInfo.value?.title || '—',
)
const courseGrade = computed(() => courseInfo.value?.grade ?? '')

const updatedLabel = computed(() => formatLastSeen(quiz.created_at))

const needsReview = computed(
  () => !quiz.is_published && questions.value.length > 0 && !isNew.value,
)

const detailKpiItems = computed(() => {
  const attempts = resultsData.value?.attempts || []
  const latest = [...attempts]
    .filter((a) => a.submitted_at)
    .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]

  const duration =
    quiz.duration_minutes && Number(quiz.duration_minutes) >= 1
      ? t('teacher.labels.durationShort', { n: quiz.duration_minutes })
      : t('teacher.status.unlimited')

  const avg =
    analytics.value?.average_score != null
      ? `${Math.round(Number(analytics.value.average_score))}%`
      : '—'

  return [
    { key: 'questions', value: questions.value.length, label: t('teacher.quizzes.questionCount') },
    { key: 'attempts', value: quiz.attempt_count || 0, label: t('teacher.quizzes.attemptCount') },
    { key: 'avg', value: avg, label: t('teacher.quizzes.avgResults') },
    { key: 'last', value: latest ? formatLastSeen(latest.submitted_at) : '—', label: t('teacher.quizzes.lastAttempt') },
    { key: 'duration', value: duration, label: t('teacher.quizzes.testTime') },
  ]
})

function scrollToForm() {
  document.getElementById('quiz-form-workspace')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function loadCourseInfo() {
  try {
    const list = await fetchTeacherCourses()
    courseInfo.value = list.find((c) => Number(c.id) === courseId.value) || null
  } catch {
    courseInfo.value = null
  }
}

async function loadExtras() {
  if (!quiz.id || isNew.value) return
  const [a, r] = await Promise.all([
    fetchManualQuizAnalytics(courseId.value, quiz.id).catch(() => null),
    fetchManualQuizResults(courseId.value, quiz.id).catch(() => null),
  ])
  analytics.value = a
  resultsData.value = r
}

async function togglePublish() {
  if (!quiz.id || isNew.value) return
  if (!String(quiz.title || '').trim()) {
    error.value = t('teacher.quizzes.titleRequired')
    scrollToForm()
    return
  }
  if (!validateDueAt()) {
    error.value = dueAtError.value
    scrollToForm()
    return
  }
  publishToggling.value = true
  error.value = ''
  const previous = quiz.is_published
  quiz.is_published = !previous
  try {
    await updateManualQuiz(courseId.value, quiz.id, buildQuizPayload())
    saved.value = true
  } catch (e) {
    quiz.is_published = previous
    error.value = getErrorMessage(e, t('teacher.errors.updatePublish'))
  } finally {
    publishToggling.value = false
  }
}

const editorMenuProps = {
  zIndex: 2600,
  contentClass: 'tds-workspace-select-menu',
}

const correctAnswerItems = computed(() =>
  questionForm.options.map((o, i) => ({
    title: String(o || '').trim() || t('teacher.labels.optionNumber', { n: i + 1 }),
    value: i,
  })),
)

function setQuestionType(type) {
  if (editingQuestionId.value || questionForm.question_type === type) return
  questionForm.question_type = type
  if (type === 'multiple_choice') {
    questionForm.options = ['', '', '', '']
    questionForm.correct_index = 0
  } else if (type === 'true_false') {
    questionForm.correct_bool = true
  } else if (type === 'short_answer') {
    questionForm.correct_text = ''
  }
}

function typeLabel(questionType) {
  const key = `teacher.quizzes.types.${questionType}`
  const label = t(key)
  return label !== key ? label : questionType
}

function validateDueAt() {
  dueAtError.value = ''
  if (!dueAtLocal.value) return true
  const d = new Date(dueAtLocal.value)
  if (Number.isNaN(d.getTime()) || d <= new Date()) {
    dueAtError.value = t('teacher.quizzes.deadlineFuture')
    return false
  }
  return true
}

function buildDueAt() {
  if (!dueAtLocal.value) return null
  const d = new Date(dueAtLocal.value)
  if (Number.isNaN(d.getTime())) {
    throw new Error(t('teacher.quizzes.deadlineInvalid'))
  }
  return d.toISOString()
}

function buildQuizPayload() {
  const passing = Number(quiz.passing_score_percent)
  const duration = Number(quiz.duration_minutes)
  return {
    title: quiz.title.trim(),
    description: quiz.description?.trim() || null,
    duration_minutes: Number.isFinite(duration) && duration >= 1 ? Math.floor(duration) : null,
    passing_score_percent: Number.isFinite(passing)
      ? Math.min(100, Math.max(0, Math.floor(passing)))
      : 60,
    is_published: Boolean(quiz.is_published),
    due_at: buildDueAt(),
  }
}

function loadDueLocal(iso) {
  if (!iso) {
    dueAtLocal.value = ''
    return
  }
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  dueAtLocal.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function resetQuestionForm() {
  Object.assign(questionForm, {
    question_type: 'multiple_choice',
    question_text: '',
    options: ['', '', '', ''],
    correct_index: 0,
    correct_bool: true,
    correct_text: '',
    points: 1,
  })
  questionFormError.value = ''
  editingQuestionId.value = null
}

function openAddQuestion() {
  resetQuestionForm()
  questionEditorOpen.value = true
}

function openEditQuestion(q) {
  resetQuestionForm()
  editingQuestionId.value = q.id
  questionForm.question_type = q.question_type
  questionForm.question_text = q.question_text
  questionForm.points = q.points
  if (q.question_type === 'multiple_choice') {
    const opts = [...(q.options || [])]
    while (opts.length < 4) opts.push('')
    questionForm.options = opts
    const idx = q.correct_answer?.index ?? q.correct_answer?.correct_index ?? 0
    questionForm.correct_index = Number(idx)
  } else if (q.question_type === 'true_false') {
    questionForm.correct_bool = q.correct_answer?.value ?? true
  } else if (q.question_type === 'short_answer') {
    questionForm.correct_text = q.correct_answer?.text || ''
  }
  questionEditorOpen.value = true
}

function closeQuestionEditor() {
  questionEditorOpen.value = false
  resetQuestionForm()
}

function validateQuestionForm() {
  questionFormError.value = ''
  if (!String(questionForm.question_text || '').trim()) {
    questionFormError.value = t('teacher.quizzes.questionRequired')
    return false
  }
  if (!questionForm.points || questionForm.points < 1) {
    questionFormError.value = t('teacher.quizzes.pointsMin')
    return false
  }
  if (questionForm.question_type === 'multiple_choice') {
    const opts = questionForm.options.filter((o) => String(o || '').trim())
    if (opts.length < 2) {
      questionFormError.value = t('teacher.quizzes.minTwoOptions')
      return false
    }
  }
  if (questionForm.question_type === 'short_answer' && !String(questionForm.correct_text || '').trim()) {
    questionFormError.value = t('teacher.quizzes.modelAnswerRequired')
    return false
  }
  return true
}

function buildQuestionPayload() {
  const base = {
    question_type: questionForm.question_type,
    question_text: questionForm.question_text.trim(),
    points: questionForm.points,
    sort_order: editingQuestionId.value
      ? questions.value.find((q) => q.id === editingQuestionId.value)?.sort_order ?? 0
      : questions.value.length,
  }
  if (questionForm.question_type === 'multiple_choice') {
    return {
      ...base,
      options: questionForm.options.filter((o) => String(o || '').trim()),
      correct_answer: { index: questionForm.correct_index },
    }
  }
  if (questionForm.question_type === 'true_false') {
    return { ...base, correct_answer: { value: questionForm.correct_bool } }
  }
  if (questionForm.question_type === 'short_answer') {
    return { ...base, correct_answer: { text: questionForm.correct_text.trim() } }
  }
  return { ...base, correct_answer: null }
}

async function saveQuiz() {
  if (!String(quiz.title || '').trim()) {
    error.value = t('teacher.quizzes.titleRequired')
    return
  }
  if (!validateDueAt()) {
    error.value = dueAtError.value
    return
  }
  saving.value = true
  error.value = ''
  saved.value = false
  let payload
  try {
    payload = buildQuizPayload()
  } catch (e) {
    error.value = e.message || t('teacher.quizzes.deadlineInvalid')
    saving.value = false
    return
  }
  try {
    if (isNew.value) {
      const created = await createManualQuiz(courseId.value, payload)
      if (!created?.id) {
        throw new Error(t('teacher.errors.serverNoQuizId'))
      }
      quiz.id = created.id
      try {
        await router.replace({
          name: 'teacher-quiz-builder',
          params: { courseId: String(courseId.value), quizId: String(created.id) },
        })
      } catch (navErr) {
        if (!isNavigationFailure(navErr)) {
          throw navErr
        }
      }
      await loadDetail()
      await loadExtras()
      saved.value = true
    } else {
      await updateManualQuiz(courseId.value, quiz.id, payload)
      saved.value = true
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveQuizSettings'))
  } finally {
    saving.value = false
  }
}

async function saveQuestion() {
  if (!validateQuestionForm()) return
  savingQuestion.value = true
  try {
    const payload = buildQuestionPayload()
    if (editingQuestionId.value) {
      await updateManualQuestion(courseId.value, quiz.id, editingQuestionId.value, payload)
    } else {
      await addManualQuestion(courseId.value, quiz.id, payload)
    }
    closeQuestionEditor()
    await loadDetail()
    await loadExtras()
  } catch (e) {
    questionFormError.value = getErrorMessage(e, t('teacher.errors.saveQuestion'))
  } finally {
    savingQuestion.value = false
  }
}

async function removeQuestion(questionId) {
  if (!confirm(t('teacher.quizzes.deleteQuestionConfirm'))) return
  try {
    await deleteManualQuestion(courseId.value, quiz.id, questionId)
    await loadDetail()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.delete'))
  }
}

async function loadDetail() {
  const data = await fetchManualQuizDetail(courseId.value, quiz.id)
  Object.assign(quiz, {
    id: data.id,
    title: data.title,
    description: data.description,
    duration_minutes: data.duration_minutes,
    passing_score_percent: data.passing_score_percent,
    is_published: data.is_published,
    due_at: data.due_at,
    total_points: data.total_points ?? 0,
    attempt_count: data.attempt_count ?? 0,
    created_at: data.created_at,
  })
  loadDueLocal(data.due_at)
  questions.value = data.questions || []
}

onMounted(async () => {
  await loadCourseInfo()
  if (isNew.value) {
    loading.value = false
    return
  }
  await loadExistingQuiz()
})

watch(
  () => route.params.quizId,
  async (nextId, prevId) => {
    if (!nextId || nextId === 'new' || nextId === prevId) return
    quiz.id = Number(nextId)
    loading.value = true
    await loadExistingQuiz()
  },
)

async function loadExistingQuiz() {
  try {
    quiz.id = Number(quizIdParam.value)
    await loadDetail()
    await loadExtras()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadQuiz'))
  } finally {
    loading.value = false
  }
}

watch(questionEditorOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

