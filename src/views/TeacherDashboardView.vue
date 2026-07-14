<template>
  <div class="teacher-home slide-up-enter-active">
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" />

    <template v-else>
      <TeacherDashboardHero :name="teacherName" />

      <TeacherQuickActions />

      <TeacherDashboardTaskSection
        section-class="teacher-home__section--action-now"
        :eyebrow="t('dashboard.teacherHome.priorityEyebrow')"
        :title="t('dashboard.teacherHome.actionNowTitle')"
        :subtitle="t('dashboard.teacherHome.actionNowSubtitle')"
        :items="actionNowItems"
        :empty-title="t('dashboard.teacherHome.actionNowEmptyTitle')"
        :empty-description="t('dashboard.teacherHome.actionNowEmptyDesc')"
      />

      <TeacherDashboardTaskSection
        section-class="teacher-home__section--important-today"
        :eyebrow="t('dashboard.teacherHome.followUpEyebrow')"
        :title="t('dashboard.teacherHome.todayTasksTitle')"
        :subtitle="t('dashboard.teacherHome.todayTasksSubtitle')"
        :items="importantTodayItems"
        empty-icon="mdi-calendar-check-outline"
        :empty-title="t('dashboard.teacherHome.todayEmptyTitle')"
        :empty-description="t('dashboard.teacherHome.todayEmptyDesc')"
      />

      <TeacherOverviewSection :metrics="overviewMetrics" />

      <div class="teacher-home__split">
        <TeacherClassesSection :courses="courses" />
        <TeacherActivitySection :items="activityItems" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../components/common/LoadingState.vue'
import TeacherDashboardHero from '../components/teacher/dashboard/TeacherDashboardHero.vue'
import TeacherDashboardTaskSection from '../components/teacher/dashboard/TeacherDashboardTaskSection.vue'
import TeacherQuickActions from '../components/teacher/dashboard/TeacherQuickActions.vue'
import TeacherClassesSection from '../components/teacher/dashboard/TeacherClassesSection.vue'
import TeacherActivitySection from '../components/teacher/dashboard/TeacherActivitySection.vue'
import TeacherOverviewSection from '../components/teacher/dashboard/TeacherOverviewSection.vue'
import {
  fetchTeacherCourseDetail,
  fetchTeacherGrades,
  fetchTeacherOverview,
} from '../api/teacherDashboard.js'
import { fetchTeacherManualQuizzes } from '../api/manualQuizzes.js'
import { fetchConversationsUnreadCount } from '../api/messages.js'
import { getErrorMessage } from '../api/client.js'
import { useAuth } from '../composables/useAuth.js'
import { enrichActivityItem } from '../utils/teacherDashboardUi.js'
import { ROUTES } from '../constants/app.js'
import '../assets/styles/teacher-home.css'

const LOW_COMPLETION_THRESHOLD = 40
const INACTIVE_DAYS = 14
const UPCOMING_QUIZ_MS = 7 * 24 * 60 * 60 * 1000

const { user } = useAuth()
const { t } = useI18n()
const teacherName = computed(() => user.value?.name || t('dashboard.teacherHome.teacherFallback'))

const loading = ref(true)
const error = ref('')
const overview = ref({ kpis: [], recent_activity: [], subscription_summary: {} })
const courses = ref([])
const unreadMessages = ref(0)

const subscriptionSummary = computed(() => overview.value?.subscription_summary || {})

const overviewMetrics = computed(() => {
  const kpis = overview.value?.kpis || []
  return kpis.map((k) => ({
    id: k.id,
    title: k.title,
    value: k.value,
    subtitle: k.subtitle || '',
    icon: k.icon || 'mdi-chart-line',
  }))
})

const totalPendingAttempts = computed(() =>
  courses.value.reduce((sum, c) => sum + (c.pending_attempts || 0), 0),
)

const actionNowItems = computed(() => {
  const items = []

  if (unreadMessages.value > 0) {
    const n = unreadMessages.value
    items.push({
      id: 'unread-messages',
      title: n === 1 ? t('dashboard.teacherHome.unreadMessagesOne') : t('dashboard.teacherHome.unreadMessagesMany', { count: n }),
      message: t('dashboard.teacherHome.unreadMessagesBody'),
      actionLabel: t('dashboard.teacherHome.openMessages'),
      actionIcon: 'mdi-message-text-outline',
      to: ROUTES.TEACHER_MESSAGES,
      variant: 'warning',
      actionVariant: 'primary',
    })
  }

  if (totalPendingAttempts.value > 0) {
    const n = totalPendingAttempts.value
    items.push({
      id: 'quiz-review',
      title: n === 1 ? t('dashboard.teacherHome.quizReviewOne') : t('dashboard.teacherHome.quizReviewMany', { count: n }),
      message: t('dashboard.teacherHome.quizReviewBody'),
      actionLabel: t('dashboard.teacherHome.gradeNow'),
      actionIcon: 'mdi-clipboard-check-outline',
      to: '/teacher/quizzes',
      variant: 'error',
      actionVariant: 'primary',
    })
  }

  for (const c of courses.value) {
    if (items.length >= 6) break

    for (const lesson of c.error_lessons || []) {
      if (items.length >= 6) break
      items.push({
        id: `lesson-error-${lesson.id}`,
        title: t('dashboard.teacherHome.aiFailedTitle', { title: lesson.title }),
        message: t('dashboard.teacherHome.aiFailedBody', { grade: c.grade, subject: c.subject_name }),
        actionLabel: t('dashboard.teacherHome.reprocess'),
        actionIcon: 'mdi-refresh',
        to: {
          name: 'teacher-lesson-preview',
          params: { courseId: c.course_id, lessonId: lesson.id },
        },
        variant: 'error',
        actionVariant: 'primary',
      })
    }

    if (c.lesson_count === 0) {
      items.push({
        id: `no-lessons-${c.course_id}`,
        title: t('dashboard.teacherHome.noPublishedLessonsTitle', { grade: c.grade, subject: c.subject_name }),
        message: t('dashboard.teacherHome.noPublishedLessonsBody'),
        actionLabel: t('dashboard.teacherHome.addLesson'),
        actionIcon: 'mdi-book-plus-outline',
        to: `/teacher/grades/${c.course_id}`,
        variant: 'warning',
        actionVariant: 'primary',
      })
      continue
    }

    if (!c.is_published) {
      items.push({
        id: `draft-${c.course_id}`,
        title: t('dashboard.teacherHome.draftClassTitle', { grade: c.grade, subject: c.subject_name }),
        message: t('dashboard.teacherHome.draftClassBody'),
        actionLabel: t('dashboard.teacherHome.openClass'),
        actionIcon: 'mdi-school-outline',
        to: `/teacher/grades/${c.course_id}`,
        variant: 'warning',
        actionVariant: 'primary',
      })
      continue
    }

    if (c.unpublished_quizzes > 0) {
      items.push({
        id: `quiz-draft-${c.course_id}`,
        title: t('dashboard.teacherHome.draftQuizTitle', { count: c.unpublished_quizzes, subject: c.subject_name }),
        message: t('dashboard.teacherHome.draftQuizBody'),
        actionLabel: t('dashboard.teacherHome.openQuiz'),
        actionIcon: 'mdi-clipboard-text-outline',
        to: '/teacher/quizzes',
        variant: 'info',
        actionVariant: 'primary',
      })
    }

    for (const lesson of c.draft_lessons || []) {
      if (items.length >= 6) break
      items.push({
        id: `lesson-draft-${lesson.id}`,
        title: t('dashboard.teacherHome.lessonNotReadyTitle', { title: lesson.title }),
        message: t('dashboard.teacherHome.lessonNotReadyBody', { grade: c.grade, subject: c.subject_name }),
        actionLabel: t('dashboard.teacherHome.editLesson'),
        actionIcon: 'mdi-pencil-outline',
        to: {
          name: 'teacher-lesson-edit',
          params: { courseId: c.course_id, lessonId: lesson.id },
        },
        variant: 'warning',
        actionVariant: 'primary',
      })
    }
  }

  return items.slice(0, 6)
})

const importantTodayItems = computed(() => {
  const items = []
  const sub = subscriptionSummary.value

  if (sub?.expiring_soon > 0) {
    const n = sub.expiring_soon
    const courseWithExpiry = courses.value.find((c) => (c.expiring_soon || 0) > 0)
    items.push({
      id: 'expiring',
      title: n === 1 ? t('dashboard.teacherHome.expiringSubsOne') : t('dashboard.teacherHome.expiringSubsMany', { count: n }),
      message: t('dashboard.teacherHome.expiringSubsBody'),
      actionLabel: t('dashboard.teacherHome.openClass'),
      actionIcon: 'mdi-clock-alert-outline',
      to: courseWithExpiry
        ? `/teacher/grades/${courseWithExpiry.course_id}`
        : ROUTES.TEACHER_GRADES,
      variant: 'warning',
      actionVariant: 'tonal',
    })
  }

  if (sub?.expired_subscribers > 0) {
    const n = sub.expired_subscribers
    const courseWithExpired = courses.value.find((c) => (c.expired_subscribers || 0) > 0)
    items.push({
      id: 'expired',
      title: n === 1 ? t('dashboard.teacherHome.expiredSubsOne') : t('dashboard.teacherHome.expiredSubsMany', { count: n }),
      message: t('dashboard.teacherHome.expiredSubsBody'),
      actionLabel: t('dashboard.teacherHome.openClass'),
      actionIcon: 'mdi-account-off-outline',
      to: courseWithExpired
        ? `/teacher/grades/${courseWithExpired.course_id}`
        : ROUTES.TEACHER_GRADES,
      variant: 'warning',
      actionVariant: 'tonal',
    })
  }

  for (const c of courses.value) {
    if (items.length >= 6) break

    if (c.subscribed_students > 0 && c.completion_percent < LOW_COMPLETION_THRESHOLD) {
      items.push({
        id: `low-completion-${c.course_id}`,
        title: t('dashboard.teacherHome.lowCompletionTitle', { subject: c.subject_name }),
        message: t('dashboard.teacherHome.lowCompletionBody', { percent: c.completion_percent, students: c.subscribed_students }),
        actionLabel: t('dashboard.teacherHome.followClass'),
        actionIcon: 'mdi-chart-line',
        to: `/teacher/grades/${c.course_id}`,
        variant: 'info',
        actionVariant: 'tonal',
      })
    }

    if ((c.inactive_students || 0) > 0) {
      items.push({
        id: `inactive-${c.course_id}`,
        title: t('dashboard.teacherHome.inactiveStudentsTitle', { count: c.inactive_students, subject: c.subject_name }),
        message: t('dashboard.teacherHome.inactiveStudentsBody'),
        actionLabel: t('dashboard.teacherHome.viewStudents'),
        actionIcon: 'mdi-account-school-outline',
        to: `/teacher/grades/${c.course_id}`,
        variant: 'info',
        actionVariant: 'tonal',
      })
    }

    for (const quiz of c.upcoming_quizzes || []) {
      if (items.length >= 6) break
      items.push({
        id: `quiz-due-${quiz.id}`,
        title: t('dashboard.teacherHome.upcomingQuizTitle', { title: quiz.title }),
        message: t('dashboard.teacherHome.upcomingQuizBody', { grade: c.grade, subject: c.subject_name, date: formatDueDate(quiz.due_at) }),
        actionLabel: t('dashboard.teacherHome.openQuiz'),
        actionIcon: 'mdi-calendar-clock',
        to: '/teacher/quizzes',
        variant: 'info',
        actionVariant: 'tonal',
      })
    }
  }

  return items.slice(0, 6)
})

const activityItems = computed(() =>
  (overview.value?.recent_activity || []).map((line, idx) => enrichActivityItem(line, idx)),
)

function formatDueDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function isInactiveStudent(student) {
  if (!student?.last_activity_at) return true
  const days = (Date.now() - new Date(student.last_activity_at).getTime()) / (24 * 60 * 60 * 1000)
  return days > INACTIVE_DAYS
}

function collectUpcomingQuizzes(quizzes) {
  const now = Date.now()
  return (quizzes || []).filter((q) => {
    if (!q.is_published || !q.due_at) return false
    const due = new Date(q.due_at).getTime()
    return due > now && due - now <= UPCOMING_QUIZ_MS
  })
}

async function enrichCoursesWithMeta(courseList) {
  const enriched = await Promise.all(
    courseList.map(async (course) => {
      try {
        const [quizzes, detail] = await Promise.all([
          fetchTeacherManualQuizzes(course.course_id),
          fetchTeacherCourseDetail(course.course_id),
        ])

        const pendingAttempts = quizzes.reduce((sum, q) => sum + (Number(q.attempt_count) || 0), 0)
        const unpublishedQuizzes = quizzes.filter((q) => !q.is_published).length
        const lessons = detail?.lessons || []
        const students = detail?.students || []

        return {
          ...course,
          quiz_count: quizzes.length,
          pending_attempts: pendingAttempts,
          unpublished_quizzes: unpublishedQuizzes,
          error_lessons: lessons.filter((l) => l.status === 'error'),
          draft_lessons: lessons.filter((l) => l.status === 'draft'),
          inactive_students: students.filter(isInactiveStudent).length,
          upcoming_quizzes: collectUpcomingQuizzes(quizzes),
          expiring_soon: detail?.analytics?.expiring_soon || 0,
          expired_subscribers: detail?.analytics?.expired_subscribers || 0,
        }
      } catch {
        return {
          ...course,
          quiz_count: 0,
          pending_attempts: 0,
          unpublished_quizzes: 0,
          error_lessons: [],
          draft_lessons: [],
          inactive_students: 0,
          upcoming_quizzes: [],
          expiring_soon: 0,
          expired_subscribers: 0,
        }
      }
    }),
  )

  return enriched
}

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const [overviewData, gradesData, unreadData] = await Promise.all([
      fetchTeacherOverview(),
      fetchTeacherGrades().catch(() => ({ courses: [] })),
      fetchConversationsUnreadCount().catch(() => ({ unread_count: 0 })),
    ])

    overview.value = overviewData
    unreadMessages.value = unreadData?.unread_count ?? 0
    const rawCourses = gradesData?.courses || []
    courses.value = rawCourses.length ? await enrichCoursesWithMeta(rawCourses) : []
  } catch (e) {
    error.value = getErrorMessage(e, t('dashboard.teacherHome.loadFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>
