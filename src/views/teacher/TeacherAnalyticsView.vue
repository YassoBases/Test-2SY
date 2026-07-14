<template>
  <TeacherWorkspaceShell mode="page" class="teacher-analytics slide-up-enter-active">
    <TeacherHero
      variant="compact"
      :eyebrow="$t('teacher.analytics.eyebrow')"
      :title="$t('teacher.analytics.title')"
    >
      <template #actions>
        <TeacherButtonGroup>
          <TeacherButton variant="tonal" :to="{ name: 'teacher-grades' }">
            {{ $t('teacher.labels.classes') }}
          </TeacherButton>
          <TeacherButton variant="ghost" :to="{ name: 'teacher-students' }">
            {{ $t('teacher.labels.students') }}
          </TeacherButton>
        </TeacherButtonGroup>
      </template>
    </TeacherHero>

    <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">{{ error }}</v-alert>
    <v-progress-linear v-if="loading" indeterminate color="primary" />

    <template v-if="!loading">
      <TeacherSummaryGrid
        v-if="overviewStatCards.length"
        :columns="overviewGridColumns"
        class="teacher-analytics__kpis"
        :aria-label="$t('teacher.analytics.kpiAria')"
      >
        <TeacherStatCard
          v-for="kpi in overviewStatCards"
          :key="kpi.id"
          compact
          :label="kpi.label"
          :value="kpi.value"
          :subtitle="kpi.subtitle"
          :icon="kpi.icon"
          :tone="kpi.tone"
          value-dir="ltr"
        />
      </TeacherSummaryGrid>

      <section
        v-if="needsAttention.length"
        aria-labelledby="analytics-attention-alerts"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-attention-alerts" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.needsAttention') }}
        </h2>
        <div class="teacher-analytics__alerts">
          <div
            v-for="(item, index) in needsAttention"
            :key="index"
            class="teacher-analytics__alert-row"
          >
            <TeacherWarningCard
              :variant="item.variant"
              :title="item.title"
              :message="item.message"
            />
            <TeacherButton
              size="small"
              variant="tonal"
              :to="item.actionTo"
            >
              {{ item.actionLabel }}
            </TeacherButton>
          </div>
        </div>
      </section>

      <TeacherEmptyStateCard
        v-if="!enrichedCourses.length"
        icon="mdi-book-education-outline"
        :title="$t('teacher.analytics.noClasses')"
        :action-label="$t('teacher.labels.classes')"
        action-to="/teacher/grades"
      />

      <section
        v-if="topPerformingClasses.length"
        aria-labelledby="analytics-top-classes-title"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-top-classes-title" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.topClasses') }}
        </h2>
        <div class="teacher-analytics__class-grid">
          <article
            v-for="course in topPerformingClasses"
            :key="`top-${course.course_id}`"
            class="teacher-analytics__class-card"
          >
            <h3 class="teacher-analytics__class-title">{{ classDisplayName(course) }}</h3>
            <div class="teacher-analytics__metric-row" :aria-label="$t('teacher.analytics.classMetricsAria')">
              <span class="teacher-analytics__metric" :title="$t('teacher.labels.students')">
                <span class="teacher-analytics__metric-icon" aria-hidden="true">👨‍🎓</span>
                <span dir="ltr">{{ course.subscribed_students }}</span>
              </span>
              <span class="teacher-analytics__metric" :title="$t('teacher.analytics.lessonCompletion')">
                <span class="teacher-analytics__metric-icon" aria-hidden="true">📚</span>
                <span dir="ltr">{{ course.completion_percent }}%</span>
              </span>
              <span class="teacher-analytics__metric" :title="$t('teacher.analytics.avgQuiz')">
                <span class="teacher-analytics__metric-icon" aria-hidden="true">📝</span>
                <span dir="ltr">{{ formatQuizCompact(course.avgQuizScore ?? course.avg_quiz_percent) }}</span>
              </span>
            </div>
            <TeacherButton
              size="small"
              variant="tonal"
              block
              :to="{ name: 'teacher-grade-detail', params: { courseId: course.course_id } }"
            >
              {{ $t('teacher.actions.openClass') }}
            </TeacherButton>
          </article>
        </div>
      </section>

      <section
        v-if="classesNeedingAttention.length"
        aria-labelledby="analytics-attention-classes-title"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-attention-classes-title" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.classesNeedAttention') }}
        </h2>
        <div class="teacher-analytics__class-grid">
          <article
            v-for="course in classesNeedingAttention"
            :key="`attention-${course.course_id}`"
            class="teacher-analytics__class-card teacher-analytics__class-card--attention"
          >
            <h3 class="teacher-analytics__class-title">{{ classDisplayName(course) }}</h3>
            <div class="teacher-analytics__metric-row" :aria-label="$t('teacher.analytics.classMetricsAria')">
              <span
                v-if="course.inactiveStudents > 0"
                class="teacher-analytics__metric teacher-analytics__metric--warn"
                :title="$t('teacher.status.inactive')"
              >
                <span class="teacher-analytics__metric-icon" aria-hidden="true">⚠</span>
                <span dir="ltr">{{ course.inactiveStudents }}</span>
              </span>
              <span class="teacher-analytics__metric" :title="$t('teacher.analytics.lessonCompletion')">
                <span class="teacher-analytics__metric-icon" aria-hidden="true">📚</span>
                <span dir="ltr">{{ course.completion_percent }}%</span>
              </span>
              <span class="teacher-analytics__metric" :title="$t('teacher.analytics.avgQuiz')">
                <span class="teacher-analytics__metric-icon" aria-hidden="true">📝</span>
                <span dir="ltr">{{ formatQuizCompact(course.avgQuizScore ?? course.avg_quiz_percent) }}</span>
              </span>
            </div>
            <TeacherButton
              size="small"
              variant="tonal"
              block
              :to="{ name: 'teacher-grade-detail', params: { courseId: course.course_id } }"
            >
              {{ $t('teacher.actions.followClass') }}
            </TeacherButton>
          </article>
        </div>
      </section>

      <section
        v-if="quizRows.length"
        aria-labelledby="analytics-quizzes-title"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-quizzes-title" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.quizPerformance') }}
        </h2>
        <TeacherWorkspaceCard flush :aria-label="$t('teacher.analytics.quizPerformance')">
          <TeacherTable>
            <thead>
              <tr>
                <th>{{ $t('teacher.labels.quiz') }}</th>
                <th>{{ $t('teacher.labels.grade') }}</th>
                <th>📝</th>
                <th>📚</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in quizRowsLimited" :key="`${row.courseId}-${row.quizId}`">
                <td class="tds-table__cell-strong text-truncate">{{ row.title }}</td>
                <td class="tds-table__cell-muted text-truncate">{{ row.classLabel }}</td>
                <td dir="ltr">{{ formatQuizCompact(row.averageScore) }}</td>
                <td dir="ltr">{{ formatQuizCompact(row.completionRate) }}</td>
              </tr>
            </tbody>
          </TeacherTable>
        </TeacherWorkspaceCard>
      </section>

      <section
        v-if="lessonRows.length"
        aria-labelledby="analytics-lessons-title"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-lessons-title" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.lessonPerformance') }}
        </h2>
        <TeacherWorkspaceCard flush :aria-label="$t('teacher.analytics.lessonPerformance')">
          <TeacherTable>
            <thead>
              <tr>
                <th>{{ $t('teacher.labels.lesson') }}</th>
                <th>{{ $t('teacher.labels.grade') }}</th>
                <th>📚</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="lesson in lessonRowsLimited"
                :key="`${lesson.courseId}-${lesson.id}`"
              >
                <td class="tds-table__cell-strong text-truncate">{{ lesson.title }}</td>
                <td class="tds-table__cell-muted text-truncate">{{ lesson.classLabel }}</td>
                <td dir="ltr">{{ lesson.completionPercent }}%</td>
              </tr>
            </tbody>
          </TeacherTable>
        </TeacherWorkspaceCard>
      </section>

      <section
        v-if="recentActivityRows.length"
        aria-labelledby="analytics-activity-title"
        class="teacher-analytics__section"
      >
        <h2 id="analytics-activity-title" class="teacher-analytics__section-title">
          {{ $t('teacher.analytics.recentActivity') }}
        </h2>
        <TeacherWorkspaceCard flush :aria-label="$t('teacher.analytics.recentActivity')">
          <ul class="teacher-analytics__activity-list">
            <li v-for="(line, index) in recentActivityLimited" :key="index">
              {{ line }}
            </li>
          </ul>
        </TeacherWorkspaceCard>
      </section>
    </template>
  </TeacherWorkspaceShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { fetchTeacherGrades, fetchTeacherCourseDetail, fetchTeacherOverview } from '../../api/teacherDashboard.js'
import { fetchCourseManualQuizAnalytics, fetchTeacherManualQuizzes } from '../../api/manualQuizzes.js'
import { fetchConversationsUnreadCount } from '../../api/messages.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
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

const PASSING_THRESHOLD = 60
const LOW_COMPLETION_THRESHOLD = 40
const INACTIVE_DAYS = 14
const TABLE_ROW_LIMIT = 6
const ACTIVITY_LIMIT = 5

const loading = ref(true)
const error = ref('')
const overview = ref(null)
const grades = ref({ courses: [] })
const courseExtras = ref(new Map())
const unreadMessages = ref(0)

const courses = computed(() => grades.value?.courses || [])

const publishedQuizCount = computed(() => {
  let total = 0
  for (const extra of courseExtras.value.values()) {
    total += (extra.manualQuizzes || []).filter((q) => q.is_published).length
  }
  return total
})

const overviewStatCards = computed(() => {
  const cards = []
  const kpiMap = Object.fromEntries((overview.value?.kpis || []).map((kpi) => [kpi.id, kpi]))
  const iconTone = {
    courses: 'primary',
    students: 'secondary',
    lessons: 'primary',
    completion: 'success',
    quizzes: 'primary',
    messages: 'warning',
  }

  const defs = [
    { id: 'courses', label: t('teacher.analytics.kpiClasses'), icon: 'mdi-school-outline', value: courses.value.length ? String(courses.value.length) : kpiMap.courses?.value },
    { id: 'students', label: t('teacher.analytics.kpiStudents'), icon: 'mdi-account-group', value: kpiMap.students?.value },
    { id: 'lessons', label: t('teacher.analytics.kpiLessons'), icon: 'mdi-play-box-multiple', value: kpiMap.lessons?.value },
    { id: 'completion', label: t('teacher.analytics.kpiCompletion'), icon: 'mdi-chart-line', value: kpiMap.completion?.value },
  ]

  for (const def of defs) {
    if (def.value == null || def.value === '') continue
    const raw = kpiMap[def.id]
    cards.push({
      id: def.id,
      label: def.label,
      value: def.value,
      icon: def.icon,
      tone: iconTone[def.id] || 'primary',
      subtitle: raw ? kpiTrendSubtitle(raw) : '',
    })
  }

  if (publishedQuizCount.value > 0) {
    cards.push({
      id: 'quizzes',
      label: t('teacher.analytics.kpiQuizzes'),
      value: String(publishedQuizCount.value),
      icon: 'mdi-clipboard-text-outline',
      tone: 'primary',
      subtitle: '',
    })
  }

  if (unreadMessages.value > 0) {
    cards.push({
      id: 'messages',
      label: t('teacher.analytics.kpiMessages'),
      value: String(unreadMessages.value),
      icon: 'mdi-message-text-outline',
      tone: 'warning',
      subtitle: '',
    })
  }

  return cards
})

const overviewGridColumns = computed(() => {
  const count = overviewStatCards.value.length
  if (count <= 2) return 2
  if (count === 3) return 3
  return Math.min(count, 4)
})

function kpiTrendSubtitle(kpi) {
  const trend = kpi.change_percent ?? kpi.trend_percent ?? kpi.comparison_percent
  if (trend == null || trend === '' || !Number.isFinite(Number(trend))) return ''
  const n = Number(trend)
  const arrow = n > 0 ? '↑' : n < 0 ? '↓' : ''
  const signed = n > 0 ? `+${n}%` : `${n}%`
  return arrow ? `${arrow} ${signed}` : signed
}

function isInactiveStudent(student) {
  if (!student?.last_activity_at) return true
  const days = (Date.now() - new Date(student.last_activity_at).getTime()) / (24 * 60 * 60 * 1000)
  return days > INACTIVE_DAYS
}

function combinedClassScore(course) {
  const completion = Number(course.completion_percent) || 0
  const quizRaw = course.avgQuizScore ?? course.avg_quiz_percent
  const quiz = quizRaw != null && quizRaw !== '' ? Number(quizRaw) : null
  if (quiz != null && Number.isFinite(quiz)) return (completion + quiz) / 2
  return completion
}

function classDisplayName(course) {
  return t('teacher.analytics.classDisplay', { grade: course.grade, subject: course.subject_name })
}

function classNeedsAttention(course) {
  if (!course.is_published) return true
  if (course.lesson_count === 0) return true
  if (course.unpublishedQuizzes > 0) return true
  if (course.subscribed_students === 0 && course.lesson_count > 0) return true
  if (course.subscribed_students > 0 && course.completion_percent < LOW_COMPLETION_THRESHOLD) return true
  if (course.inactiveStudents > 0) return true
  const quizAvg = course.avgQuizScore ?? course.avg_quiz_percent
  if (
    course.subscribed_students > 0
    && quizAvg != null
    && quizAvg !== ''
    && Number(quizAvg) < PASSING_THRESHOLD
  ) {
    return true
  }
  return false
}

const enrichedCourses = computed(() =>
  courses.value.map((course) => {
    const extra = courseExtras.value.get(course.course_id) || {}
    const detail = extra.detail
    const quizAnalytics = extra.quizAnalytics
    const manualQuizzes = extra.manualQuizzes || []
    const detailStudents = detail?.students || []

    return {
      ...course,
      classLabel: t('teacher.analytics.classLabel', { subject: course.subject_name, grade: course.grade }),
      avgQuizScore: quizAnalytics?.average_score ?? null,
      inactiveStudents: detailStudents.filter(isInactiveStudent).length,
      unpublishedQuizzes: manualQuizzes.filter((quiz) => !quiz.is_published).length,
    }
  }),
)

const topPerformingClasses = computed(() =>
  [...enrichedCourses.value]
    .sort((a, b) => combinedClassScore(b) - combinedClassScore(a))
    .slice(0, 5),
)

const classesNeedingAttention = computed(() =>
  enrichedCourses.value
    .filter(classNeedsAttention)
    .sort((a, b) => {
      const completionDiff =
        (Number(a.completion_percent) || 0) - (Number(b.completion_percent) || 0)
      if (completionDiff !== 0) return completionDiff
      const aq = Number(a.avgQuizScore ?? a.avg_quiz_percent ?? 100)
      const bq = Number(b.avgQuizScore ?? b.avg_quiz_percent ?? 100)
      if (aq !== bq) return aq - bq
      return (b.inactiveStudents || 0) - (a.inactiveStudents || 0)
    }),
)

const quizRows = computed(() => {
  const rows = []
  for (const course of courses.value) {
    const extra = courseExtras.value.get(course.course_id)
    const classLabel = `${course.subject_name} · ${course.grade}`
    for (const quiz of extra?.quizAnalytics?.quizzes || []) {
      rows.push({
        quizId: quiz.quiz_id,
        title: quiz.quiz_title,
        courseId: course.course_id,
        classLabel,
        averageScore: quiz.average_score,
        completionRate: quiz.completion_rate,
        attemptedCount: quiz.attempted_count,
      })
    }
  }
  return rows
})

const quizRowsLimited = computed(() =>
  [...quizRows.value]
    .sort((a, b) => (a.averageScore ?? -1) - (b.averageScore ?? -1))
    .slice(0, TABLE_ROW_LIMIT),
)

const weakestQuiz = computed(() => {
  const scored = quizRows.value.filter((q) => q.averageScore != null && q.attemptedCount > 0)
  if (!scored.length) return null
  return [...scored].sort((a, b) => a.averageScore - b.averageScore)[0]
})

const lessonRows = computed(() => {
  const rows = []
  for (const course of courses.value) {
    const detail = courseExtras.value.get(course.course_id)?.detail
    const classLabel = `${course.subject_name} · ${course.grade}`
    for (const lesson of detail?.lessons || []) {
      rows.push({
        id: lesson.id,
        title: lesson.title,
        courseId: course.course_id,
        classLabel,
        completionPercent: lesson.completion_percent ?? 0,
      })
    }
  }
  return rows
})

const lessonRowsLimited = computed(() =>
  [...lessonRows.value]
    .sort((a, b) => a.completionPercent - b.completionPercent)
    .slice(0, TABLE_ROW_LIMIT),
)

const bottomLesson = computed(() => {
  if (!lessonRows.value.length) return null
  return [...lessonRows.value].sort((a, b) => a.completionPercent - b.completionPercent)[0]
})

const recentActivityRows = computed(() => overview.value?.recent_activity || [])

const recentActivityLimited = computed(() => recentActivityRows.value.slice(0, ACTIVITY_LIMIT))

const needsAttention = computed(() => {
  const items = []
  const sub = overview.value?.subscription_summary

  if (sub?.expiring_soon > 0) {
    items.push({
      variant: 'warning',
      title: t('teacher.analytics.subsExpiringTitle'),
      message: t('teacher.analytics.subsExpiringCount', { count: sub.expiring_soon }),
      actionLabel: t('teacher.actions.openClasses'),
      actionTo: { name: 'teacher-grades' },
    })
  }

  if (sub?.expired_subscribers > 0) {
    items.push({
      variant: 'warning',
      title: t('teacher.analytics.subsExpiredTitle'),
      message: t('teacher.analytics.subsExpiredCount', { count: sub.expired_subscribers }),
      actionLabel: t('teacher.actions.openClasses'),
      actionTo: { name: 'teacher-grades' },
    })
  }

  if (weakestQuiz.value && weakestQuiz.value.averageScore < PASSING_THRESHOLD) {
    items.push({
      variant: 'warning',
      title: t('teacher.analytics.weakQuizTitle', { title: weakestQuiz.value.title }),
      message: `${formatQuizCompact(weakestQuiz.value.averageScore)} · ${weakestQuiz.value.classLabel}`,
      actionLabel: t('teacher.actions.openResults'),
      actionTo: {
        name: 'teacher-quiz-results',
        params: { courseId: weakestQuiz.value.courseId, quizId: weakestQuiz.value.quizId },
      },
    })
  }

  if (bottomLesson.value && bottomLesson.value.completionPercent < LOW_COMPLETION_THRESHOLD) {
    items.push({
      variant: 'info',
      title: t('teacher.analytics.skippedLessonTitle', { title: bottomLesson.value.title }),
      message: `${bottomLesson.value.completionPercent}% · ${bottomLesson.value.classLabel}`,
      actionLabel: t('teacher.actions.openLesson'),
      actionTo: {
        name: 'teacher-lesson-preview',
        params: { courseId: bottomLesson.value.courseId, lessonId: bottomLesson.value.id },
      },
    })
  }

  if (unreadMessages.value > 0) {
    items.push({
      variant: 'warning',
      title: unreadMessages.value === 1 ? t('teacher.analytics.unreadMessage') : t('teacher.analytics.unreadMessagesCount', { count: unreadMessages.value }),
      message: t('teacher.analytics.awaitingReply'),
      actionLabel: t('teacher.actions.openMessages'),
      actionTo: ROUTES.TEACHER_MESSAGES,
    })
  }

  return items.slice(0, 6)
})

function formatQuizCompact(value) {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  return `${n % 1 === 0 ? n : n.toFixed(0)}%`
}

async function loadCourseExtras(courseId) {
  const [detail, quizAnalytics, manualQuizzes] = await Promise.all([
    fetchTeacherCourseDetail(courseId).catch(() => null),
    fetchCourseManualQuizAnalytics(courseId).catch(() => null),
    fetchTeacherManualQuizzes(courseId).catch(() => []),
  ])
  courseExtras.value.set(courseId, { detail, quizAnalytics, manualQuizzes: manualQuizzes || [] })
}

async function load() {
  loading.value = true
  error.value = ''
  courseExtras.value = new Map()

  try {
    const [overviewData, gradesData, unreadData] = await Promise.all([
      fetchTeacherOverview(),
      fetchTeacherGrades(),
      fetchConversationsUnreadCount().catch(() => ({ unread_count: 0 })),
    ])

    overview.value = overviewData
    grades.value = gradesData
    unreadMessages.value = unreadData?.unread_count ?? 0

    const ids = (gradesData.courses || []).map((c) => c.course_id)
    await Promise.all(ids.map((id) => loadCourseExtras(id)))
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadAnalytics'))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.teacher-analytics__kpis {
  margin-bottom: var(--em-space-lg);
}

.teacher-analytics__section {
  margin-top: var(--em-space-xl);
}

.teacher-analytics__section-title {
  margin: 0 0 var(--em-space-lg);
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.02em;
  color: var(--em-text);
}

.teacher-analytics__class-grid {
  display: grid;
  gap: var(--em-space-lg);
}

@media (min-width: 640px) {
  .teacher-analytics__class-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1100px) {
  .teacher-analytics__class-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.teacher-analytics__class-card {
  display: flex;
  flex-direction: column;
  gap: var(--em-space-md);
  padding: var(--em-space-lg);
  border-radius: var(--em-radius-lg, 16px);
  border: 1px solid var(--em-border-subtle);
  background: var(--em-card-l1, var(--em-surface-secondary));
}

.teacher-analytics__class-card--attention {
  border-color: color-mix(in srgb, var(--em-warning, #f59e0b) 28%, var(--em-border-subtle));
}

.teacher-analytics__class-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--em-text);
}

.teacher-analytics__metric-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--em-space-md);
}

.teacher-analytics__metric {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9375rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--em-text);
}

.teacher-analytics__metric--warn {
  color: var(--em-warning, #d97706);
}

.teacher-analytics__metric-icon {
  font-size: 1rem;
  line-height: 1;
}

.teacher-analytics__alerts {
  display: flex;
  flex-direction: column;
  gap: var(--em-space-md);
}

.teacher-analytics__alert-row {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--em-space-sm);
}

@media (min-width: 640px) {
  .teacher-analytics__alert-row {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .teacher-analytics__alert-row .tds-warning-card {
    flex: 1;
    min-width: 0;
  }
}

.teacher-analytics__activity-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--em-space-sm);
}

.teacher-analytics__activity-list li {
  font-size: var(--em-text-sm);
  color: var(--em-text-muted);
  line-height: 1.45;
  padding: var(--em-space-sm) 0;
  border-bottom: 1px solid var(--em-border-subtle);
}

.teacher-analytics__activity-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.teacher-analytics .tds-workspace + .teacher-analytics__section,
.teacher-analytics__section + .tds-workspace {
  margin-top: var(--em-space-xl);
}
</style>
