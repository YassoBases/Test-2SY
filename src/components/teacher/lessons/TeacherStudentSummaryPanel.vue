<template>
  <section class="student-summary-panel">
    <header class="student-summary-panel__head">
      <h2 class="student-summary-panel__title">{{ $t('teacher.labels.students') }}</h2>
      <p class="student-summary-panel__total">{{ totalLabel }}</p>
    </header>

    <div v-if="hasStudents" class="student-summary-panel__body">
      <ul v-if="summaryLines.length" class="student-summary-panel__stats">
        <li v-for="line in summaryLines" :key="line.id" class="student-summary-panel__stat">
          {{ line.label }}
        </li>
      </ul>

      <div v-if="topStudents.length" class="student-summary-panel__group">
        <h3 class="student-summary-panel__group-title">{{ $t('teacher.students.topStudents') }}</h3>
        <div class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in topStudents"
            :key="`top-${student.student_id}`"
            :student="student"
          />
        </div>
      </div>

      <div v-if="laggingStudents.length" class="student-summary-panel__group">
        <h3 class="student-summary-panel__group-title">{{ $t('teacher.students.laggingStudents') }}</h3>
        <div class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in laggingStudents"
            :key="`lagging-${student.student_id}`"
            :student="student"
          />
        </div>
      </div>

      <div v-if="inactiveStudents.length" class="student-summary-panel__group">
        <h3 class="student-summary-panel__group-title">{{ $t('teacher.students.inactiveStudents') }}</h3>
        <div class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in inactiveStudents"
            :key="`inactive-${student.student_id}`"
            :student="student"
          />
        </div>
      </div>

      <div class="student-summary-panel__preview">
        <h3 class="student-summary-panel__preview-title">{{ $t('teacher.students.recentlyActive') }}</h3>

        <div v-if="recentStudents.length" class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in recentStudents"
            :key="student.student_id"
            :student="student"
          />
        </div>

        <p v-else class="student-summary-panel__preview-empty">
          {{ $t('teacher.students.noRecentActivity') }}
        </p>
      </div>

      <div v-if="noQuizStudents.length" class="student-summary-panel__group">
        <h3 class="student-summary-panel__group-title">{{ $t('teacher.students.noQuizTakers') }}</h3>
        <div class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in noQuizStudents"
            :key="`no-quiz-${student.student_id}`"
            :student="student"
          />
        </div>
      </div>

      <div v-if="noLessonProgressStudents.length" class="student-summary-panel__group">
        <h3 class="student-summary-panel__group-title">{{ $t('teacher.students.noLessonCompleters') }}</h3>
        <div class="student-summary-panel__rows">
          <TeacherStudentPreviewRow
            v-for="student in noLessonProgressStudents"
            :key="`no-lesson-${student.student_id}`"
            :student="student"
          />
        </div>
      </div>
    </div>

    <p v-else class="student-summary-panel__empty">
      {{ $t('teacher.students.noEnrolled') }}
    </p>

    <footer class="student-summary-panel__footer">
      <v-btn
        class="student-summary-panel__cta"
        variant="tonal"
        rounded="lg"
        block
        :to="studentsManageTo"
      >
        {{ $t('teacher.actions.manageAllStudents') }}
        <v-icon end>mdi-arrow-left</v-icon>
      </v-btn>
    </footer>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherStudentPreviewRow from './TeacherStudentPreviewRow.vue'

const LOW_PROGRESS_THRESHOLD = 40
const INACTIVE_DAYS = 14
const PREVIEW_LIMIT = 5

const props = defineProps({
  analytics: { type: Object, required: true },
  students: { type: Array, default: () => [] },
  previewLimit: { type: Number, default: PREVIEW_LIMIT },
  grade: { type: Number, default: null },
  subjectId: { type: Number, default: null },
})

const totalCount = computed(() => {
  const fromAnalytics = Number(props.analytics?.subscribed_students)
  if (Number.isFinite(fromAnalytics) && fromAnalytics > 0) return fromAnalytics
  return props.students.length
})

const hasStudents = computed(() => totalCount.value > 0)

const totalLabel = computed(() => {
  const n = totalCount.value
  if (n === 0) return t('teacher.students.noStudents')
  if (n === 1) return t('teacher.students.oneStudentCount')
  if (n === 2) return t('teacher.students.twoStudents')
  return t('teacher.labels.studentCount', { count: n })
})

const studentsManageTo = computed(() => {
  const query = {}
  if (props.grade != null) query.grade = String(props.grade)
  if (props.subjectId != null) query.subject_id = String(props.subjectId)
  return Object.keys(query).length
    ? { name: 'teacher-students', query }
    : { name: 'teacher-students' }
})

function isInactiveStudent(student) {
  if (!student?.last_activity_at) return true
  const days = (Date.now() - new Date(student.last_activity_at).getTime()) / (24 * 60 * 60 * 1000)
  return days > INACTIVE_DAYS
}

function studentScore(student) {
  const progress = Number(student.progress_percent) || 0
  const quiz = Number(student.avg_quiz_percent) || 0
  return quiz > 0 ? (progress + quiz) / 2 : progress
}

const inactiveCount = computed(() => props.students.filter(isInactiveStudent).length)

const needsFollowUpCount = computed(() => Number(props.analytics?.expired_subscribers) || 0)

const summaryLines = computed(() => {
  const lines = []
  const expiring = Number(props.analytics?.expiring_soon) || 0
  const inactive = inactiveCount.value
  const followUp = needsFollowUpCount.value

  if (expiring > 0) {
    lines.push({
      id: 'expiring',
      label: expiring === 1 ? t('teacher.students.subExpiring') : t('teacher.students.subsExpiring'),
    })
  }

  if (inactive > 0) {
    lines.push({
      id: 'inactive',
      label: inactive === 1 ? t('teacher.students.inactiveStudent') : t('teacher.status.inactive'),
    })
  }

  if (followUp > 0) {
    lines.push({
      id: 'follow-up',
      label: followUp === 1 ? t('teacher.students.needsFollowUp') : t('teacher.students.needsFollowUp'),
    })
  }

  return lines
})

const topStudents = computed(() =>
  [...props.students]
    .sort((a, b) => studentScore(b) - studentScore(a))
    .slice(0, props.previewLimit),
)

const laggingStudents = computed(() =>
  [...props.students]
    .filter((student) => (Number(student.progress_percent) || 0) < LOW_PROGRESS_THRESHOLD)
    .sort((a, b) => (Number(a.progress_percent) || 0) - (Number(b.progress_percent) || 0))
    .slice(0, props.previewLimit),
)

const inactiveStudents = computed(() =>
  props.students.filter(isInactiveStudent).slice(0, props.previewLimit),
)

const recentStudents = computed(() =>
  [...props.students]
    .filter((student) => student.last_activity_at)
    .sort((a, b) => new Date(b.last_activity_at) - new Date(a.last_activity_at))
    .slice(0, props.previewLimit),
)

const noQuizStudents = computed(() =>
  props.students
    .filter(
      (student) =>
        (Number(student.avg_quiz_percent) || 0) === 0
        && (Number(student.total_lessons) || 0) > 0,
    )
    .slice(0, props.previewLimit),
)

const noLessonProgressStudents = computed(() =>
  props.students
    .filter(
      (student) =>
        (Number(student.completed_lessons) || 0) === 0
        && (Number(student.total_lessons) || 0) > 0,
    )
    .slice(0, props.previewLimit),
)
</script>
