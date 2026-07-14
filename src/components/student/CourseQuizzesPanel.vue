<template>
  <div class="quizzes-panel pa-4 pa-md-6">
    <div class="mb-5">
      <h2 class="text-h6 font-weight-bold mb-1">{{ t('student.course.quizzes.title') }}</h2>
      <p class="text-caption text-medium-emphasis mb-0">
        {{ t('student.course.quizzes.subtitleFull') }}
      </p>
    </div>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <v-row v-if="!loading && quizzes.length">
      <v-col v-for="qz in quizzes" :key="qz.id" cols="12" md="6">
        <v-card class="glass-card pa-4 h-100 d-flex flex-column" variant="flat">
          <div class="d-flex justify-space-between align-start gap-2 mb-2">
            <h3 class="text-subtitle-1 font-weight-bold">{{ qz.title }}</h3>
            <v-chip size="small" :color="statusColor(qz)" variant="tonal">
              {{ statusLabel(qz) }}
            </v-chip>
          </div>

          <p v-if="qz.description" class="text-body-2 text-medium-emphasis mb-3 flex-grow-1">
            {{ qz.description }}
          </p>

          <div class="text-caption text-medium-emphasis mb-4">
            {{ metaLine(qz) }}
          </div>
          <div v-if="hasResult(qz) && qz.max_score != null" class="text-body-2 mb-3">
            {{ t('student.course.quizzes.yourScore') }}
            <strong>{{ qz.score }} / {{ qz.max_score }}</strong>
            <span v-if="qz.percent != null"> ({{ qz.percent }}%)</span>
          </div>

          <div class="d-flex flex-wrap gap-2">
            <v-btn
              v-if="canTake(qz)"
              color="primary"
              class="btn-glow"
              :to="ROUTES.STUDENT_MANUAL_QUIZ(qz.id, courseId)"
            >
              {{ qz.attempt_status === 'in_progress' ? t('student.course.quizzes.cta.continueQuiz') : t('student.course.quizzes.cta.startQuiz') }}
            </v-btn>
            <v-btn
              v-else-if="hasResult(qz)"
              variant="tonal"
              color="secondary"
              :to="ROUTES.STUDENT_MANUAL_QUIZ(qz.id, courseId)"
            >
              {{ t('student.course.quizzes.cta.viewResult') }}
            </v-btn>
            <v-chip v-else-if="qz.attempt_status === 'submitted'" size="small" color="warning" variant="tonal">
              {{ t('student.course.quizzes.pendingGrading') }}
            </v-chip>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card v-else-if="!loading" class="glass-card pa-10 text-center" variant="flat">
      <v-icon size="56" color="grey" class="mb-3">mdi-clipboard-text-outline</v-icon>
      <p class="text-body-1 font-weight-medium mb-2">{{ t('student.course.quizzes.empty.title') }}</p>
      <p class="text-caption text-medium-emphasis">
        {{ t('student.course.quizzes.empty.subtitle') }}
      </p>
    </v-card>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchStudentManualQuizzes } from '../../api/manualQuizzes.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()

const props = defineProps({
  courseId: { type: [Number, String], required: true },
  unlocked: { type: Boolean, default: false },
})

const loading = ref(false)
const error = ref('')
const quizzes = ref([])

function formatDue(iso) {
  try {
    return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
  } catch {
    return iso
  }
}

function metaLine(qz) {
  const duration = qz.duration_minutes ? t('student.course.quizzes.duration', { n: qz.duration_minutes }) : ''
  const due = qz.due_at ? t('student.course.quizzes.due', { date: formatDue(qz.due_at) }) : ''
  return t('student.course.quizzes.metaLine', {
    n: qz.question_count,
    points: qz.total_points || '—',
    pass: qz.passing_score_percent,
    duration,
    due,
  })
}

function statusLabel(qz) {
  if (qz.percent != null && qz.passed === true) {
    return t('student.course.quizzes.status.passed', { pct: qz.percent })
  }
  if (qz.percent != null && qz.passed === false) return `${qz.percent}%`
  if (qz.attempt_status === 'graded') {
    return qz.percent != null ? `${qz.percent}%` : t('student.course.quizzes.status.graded')
  }
  if (qz.attempt_status === 'submitted') return t('student.course.quizzes.status.submitted')
  if (qz.attempt_status === 'in_progress') return t('student.course.quizzes.status.inProgress')
  return t('student.course.quizzes.status.available')
}

function statusColor(qz) {
  if (qz.passed === true) return 'success'
  if (qz.passed === false) return 'error'
  if (qz.attempt_status === 'submitted') return 'warning'
  if (qz.attempt_status === 'in_progress') return 'info'
  return 'secondary'
}

function canTake(qz) {
  return !qz.attempt_status || qz.attempt_status === 'in_progress'
}

function hasResult(qz) {
  return qz.attempt_status === 'graded' || (qz.attempt_status === 'submitted' && qz.percent != null)
}

async function load() {
  if (!props.unlocked) {
    quizzes.value = []
    return
  }
  loading.value = true
  error.value = ''
  try {
    quizzes.value = await fetchStudentManualQuizzes(Number(props.courseId))
  } catch (e) {
    error.value = getErrorMessage(e, t('student.course.quizzes.errors.load'))
    quizzes.value = []
  } finally {
    loading.value = false
  }
}

watch(() => [props.courseId, props.unlocked], load)
onMounted(load)

defineExpose({ reload: load })
</script>
