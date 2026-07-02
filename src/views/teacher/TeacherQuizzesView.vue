<template>
  <div class="teacher-quizzes-page slide-up-enter-active">
    <PageHeader
      :eyebrow="$t('teacher.grades.eyebrow')"
      :title="$t('teacher.labels.quizzes')"
      :subtitle="$t('teacher.quizzes.subtitle')"
    >
      <template #actions>
        <v-btn
          class="btn-glow"
          rounded="lg"
          :disabled="!courses.length"
          @click="openCreate"
        >
          <v-icon start>mdi-plus</v-icon>
          {{ $t('teacher.actions.createQuiz') }}
        </v-btn>
      </template>
    </PageHeader>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="4" class="mb-4" />

    <template v-else>
      <TeacherQuizKpiStrip v-if="allQuizzes.length" :items="kpiItems" />

      <TeacherQuizWorkspaceToolbar
        v-if="courses.length"
        v-model:search="searchQuery"
        v-model:status-filter="statusFilter"
        :chips="filterChips"
      />

      <div v-if="visibleGroups.length" class="teacher-quiz-groups">
        <TeacherQuizClassGroup
          v-for="group in visibleGroups"
          :key="group.courseId"
          :course-id="group.courseId"
          :grade="group.grade"
          :subject="group.subject"
          :quizzes="group.quizzes"
          :total-count="group.totalCount"
          @delete="confirmDelete"
          @create="goToCreate(group.courseId)"
        />
      </div>

      <div v-else-if="courses.length && hasActiveFilters" class="teacher-quiz-empty teacher-quiz-empty--filtered">
        <span class="teacher-quiz-empty__icon" aria-hidden="true">
          <v-icon size="28">mdi-filter-off-outline</v-icon>
        </span>
        <h2 class="teacher-quiz-empty__title">{{ $t('teacher.quizzes.noFilterMatch') }}</h2>
        <p class="teacher-quiz-empty__desc">{{ $t('teacher.quizzes.tryOtherSearch') }}</p>
        <v-btn variant="tonal" size="small" rounded="lg" @click="resetFilters">{{ $t('teacher.actions.viewAll') }}</v-btn>
      </div>

      <div v-else-if="courses.length" class="teacher-quiz-empty">
        <span class="teacher-quiz-empty__icon" aria-hidden="true">
          <v-icon size="32">mdi-clipboard-text-outline</v-icon>
        </span>
        <h2 class="teacher-quiz-empty__title">{{ $t('teacher.quizzes.noneYet') }}</h2>
        <p class="teacher-quiz-empty__desc">
          {{ $t('teacher.quizzes.createFirstHint') }}
        </p>
        <v-btn class="btn-glow" rounded="lg" size="large" @click="openCreate">
          <v-icon start>mdi-plus</v-icon>
          {{ $t('teacher.actions.createQuiz') }}
        </v-btn>
      </div>

      <div v-else class="teacher-quiz-empty">
        <span class="teacher-quiz-empty__icon" aria-hidden="true">
          <v-icon size="32">mdi-school-outline</v-icon>
        </span>
        <h2 class="teacher-quiz-empty__title">{{ $t('teacher.actions.createClassFirst') }}</h2>
        <p class="teacher-quiz-empty__desc">
          {{ $t('teacher.quizzes.needClassFirst') }}
        </p>
        <v-btn class="btn-glow" rounded="lg" variant="tonal" to="/teacher/grades">
          {{ $t('teacher.actions.goToGrades') }}
        </v-btn>
      </div>
    </template>

    <v-dialog v-model="showCreateDialog" max-width="440">
      <v-card class="glass-card pa-5 rounded-lg" variant="flat">
        <h3 class="text-subtitle-1 font-weight-bold mb-1">{{ $t('teacher.actions.createQuiz') }}</h3>
        <p class="teacher-quiz-create-sheet__hint">{{ $t('teacher.quizzes.pickClass') }}</p>
        <div class="teacher-quiz-create-sheet__list">
          <button
            v-for="course in courses"
            :key="course.id"
            type="button"
            class="teacher-quiz-create-sheet__course"
            @click="goToCreate(course.id)"
          >
            <div>
              <p class="teacher-quiz-create-sheet__course-name">{{ course.subject_name || course.title }}</p>
              <p class="teacher-quiz-create-sheet__course-meta">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</p>
            </div>
            <v-icon size="18">mdi-arrow-left</v-icon>
          </button>
        </div>
        <v-btn variant="text" block class="mt-3" @click="showCreateDialog = false">{{ $t('common.cancel') }}</v-btn>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRouter } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import TeacherQuizClassGroup from '../../components/teacher/quizzes/TeacherQuizClassGroup.vue'
import TeacherQuizKpiStrip from '../../components/teacher/quizzes/TeacherQuizKpiStrip.vue'
import TeacherQuizWorkspaceToolbar from '../../components/teacher/quizzes/TeacherQuizWorkspaceToolbar.vue'
import { fetchTeacherCourses } from '../../api/teacherCourses.js'
import {
  deleteManualQuiz,
  fetchCourseManualQuizAnalytics,
  fetchTeacherManualQuizzes,
} from '../../api/manualQuizzes.js'
import { getErrorMessage } from '../../api/client.js'
import '../../assets/styles/teacher-quizzes.css'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const courses = ref([])
const allQuizzes = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')
const showCreateDialog = ref(false)

function courseSubject(course) {
  return course.subject_name || course.title || t('teacher.labels.subjectShort')
}

function classLabelFor(course) {
  return `${courseSubject(course)} • ${t('teacher.labels.gradeNumber', { grade: course.grade })}`
}

function courseMatchesSearch(course, q) {
  if (!q) return true
  const subject = courseSubject(course).toLowerCase()
  const grade = String(course.grade ?? '')
  const gradePhrase = t('teacher.labels.gradeNumber', { grade }).toLowerCase()
  return subject.includes(q) || grade.includes(q) || gradePhrase.includes(q)
}

function quizMatchesSearch(course, quiz, q) {
  if (!q) return true
  return (
    quiz.title?.toLowerCase().includes(q) ||
    courseMatchesSearch(course, q) ||
    classLabelFor(course).toLowerCase().includes(q)
  )
}

function passesStatusFilter(quiz) {
  if (statusFilter.value === 'published') return quiz.is_published
  if (statusFilter.value === 'draft') return !quiz.is_published
  if (statusFilter.value === 'review') return needsReview(quiz)
  if (statusFilter.value === 'ai') return false
  return true
}

function needsReview(quiz) {
  return !quiz.is_published && (quiz.question_count || 0) > 0
}

async function loadWorkspace() {
  loading.value = true
  error.value = ''
  try {
    courses.value = await fetchTeacherCourses()
    const rows = []

    await Promise.all(
      courses.value.map(async (course) => {
        const courseId = course.id
        try {
          const [quizzes, analytics] = await Promise.all([
            fetchTeacherManualQuizzes(courseId),
            fetchCourseManualQuizAnalytics(courseId).catch(() => null),
          ])

          const scoreByQuizId = new Map(
            (analytics?.quizzes || []).map((q) => [q.quiz_id, q.average_score]),
          )

          for (const quiz of quizzes) {
            rows.push({
              quiz,
              courseId,
              grade: course.grade,
              subject: courseSubject(course),
              classLabel: classLabelFor(course),
              averageScore: scoreByQuizId.get(quiz.id) ?? null,
              createdAt: quiz.created_at,
            })
          }
        } catch {
          /* skip course on partial failure */
        }
      }),
    )

    rows.sort((a, b) => {
      const ta = a.createdAt ? new Date(a.createdAt).getTime() : 0
      const tb = b.createdAt ? new Date(b.createdAt).getTime() : 0
      return tb - ta
    })

    allQuizzes.value = rows
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadQuizzes'))
  } finally {
    loading.value = false
  }
}

const filterCounts = computed(() => {
  const list = allQuizzes.value
  return {
    all: list.length,
    published: list.filter((i) => i.quiz.is_published).length,
    draft: list.filter((i) => !i.quiz.is_published).length,
    review: list.filter((i) => needsReview(i.quiz)).length,
    ai: 0,
  }
})

const filterChips = computed(() => [
  { value: 'all', label: t('common.all'), count: filterCounts.value.all },
  { value: 'published', label: t('teacher.status.published'), count: filterCounts.value.published },
  { value: 'draft', label: t('teacher.status.draft'), count: filterCounts.value.draft },
  { value: 'review', label: t('teacher.status.pendingReview'), count: filterCounts.value.review },
  { value: 'ai', label: 'AI', count: filterCounts.value.ai },
])

const kpiItems = computed(() => {
  const scores = allQuizzes.value
    .map((i) => i.averageScore)
    .filter((v) => v != null && !Number.isNaN(Number(v)))

  const avgOverall =
    scores.length > 0
      ? `${Math.round(scores.reduce((a, b) => a + Number(b), 0) / scores.length)}%`
      : '—'

  return [
    { key: 'total', value: filterCounts.value.all, label: t('teacher.quizzes.total') },
    { key: 'published', value: filterCounts.value.published, label: t('teacher.quizzes.publishedCount') },
    { key: 'draft', value: filterCounts.value.draft, label: t('teacher.quizzes.draftCount') },
    { key: 'review', value: filterCounts.value.review, label: t('teacher.status.pendingReview') },
    { key: 'avg', value: avgOverall, label: t('teacher.quizzes.avgResults') },
  ]
})

const hasActiveFilters = computed(
  () => Boolean(searchQuery.value.trim()) || statusFilter.value !== 'all',
)

const visibleGroups = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  const filtering = hasActiveFilters.value

  const groups = courses.value.map((course) => {
    const inCourse = allQuizzes.value.filter((i) => i.courseId === course.id)
    const visible = inCourse.filter(
      (item) => passesStatusFilter(item.quiz) && quizMatchesSearch(course, item.quiz, q),
    )

    return {
      courseId: course.id,
      grade: course.grade,
      subject: courseSubject(course),
      quizzes: visible.sort((a, b) => {
        const ta = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const tb = b.createdAt ? new Date(b.createdAt).getTime() : 0
        return tb - ta
      }),
      totalCount: inCourse.length,
      isEmpty: inCourse.length === 0,
      courseMatches: courseMatchesSearch(course, q),
    }
  })

  return groups
    .filter((group) => {
      if (!filtering) return true
      if (group.quizzes.length > 0) return true
      if (group.isEmpty && group.courseMatches && statusFilter.value === 'all') return true
      return false
    })
    .sort((a, b) => {
      const gradeDiff = Number(b.grade) - Number(a.grade)
      if (gradeDiff !== 0) return gradeDiff
      return a.subject.localeCompare(b.subject, 'ar')
    })
})

function resetFilters() {
  searchQuery.value = ''
  statusFilter.value = 'all'
}

function openCreate() {
  if (!courses.value.length) return
  if (courses.value.length === 1) {
    goToCreate(courses.value[0].id)
    return
  }
  showCreateDialog.value = true
}

function goToCreate(courseId) {
  showCreateDialog.value = false
  router.push({
    name: 'teacher-quiz-builder',
    params: { courseId, quizId: 'new' },
  })
}

async function confirmDelete(item) {
  if (!confirm(t('teacher.quizzes.deleteConfirmTitle', { title: item.quiz.title }))) return
  try {
    await deleteManualQuiz(item.courseId, item.quiz.id)
    allQuizzes.value = allQuizzes.value.filter(
      (row) => !(row.courseId === item.courseId && row.quiz.id === item.quiz.id),
    )
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.delete'))
  }
}

onMounted(loadWorkspace)
</script>
