<template>
  <section class="teacher-quiz-detail__section" aria-labelledby="quiz-results-summary-title">
    <div class="teacher-quiz-detail__section-head">
      <div>
        <h2 id="quiz-results-summary-title" class="teacher-quiz-detail__section-title">{{ $t('teacher.quizzes.resultsSummary') }}</h2>
        <p class="teacher-quiz-detail__section-sub">{{ $t('teacher.quizzes.resultsQuickView') }}</p>
      </div>
    </div>

    <div class="teacher-quiz-detail__results-panel">
      <div class="teacher-quiz-detail__results-stats">
        <div class="teacher-quiz-detail__results-stat">
          <p class="teacher-quiz-detail__results-stat-value" dir="ltr">{{ formatPercent(averageScore) }}</p>
          <p class="teacher-quiz-detail__results-stat-label">{{ $t('teacher.quizzes.avgResults') }}</p>
        </div>
        <div class="teacher-quiz-detail__results-stat">
          <p class="teacher-quiz-detail__results-stat-value" dir="ltr">{{ formatPercent(highestScore) }}</p>
          <p class="teacher-quiz-detail__results-stat-label">{{ $t('teacher.quizzes.highestResult') }}</p>
        </div>
        <div class="teacher-quiz-detail__results-stat">
          <p class="teacher-quiz-detail__results-stat-value" dir="ltr">{{ formatPercent(lowestScore) }}</p>
          <p class="teacher-quiz-detail__results-stat-label">{{ $t('teacher.students.lowestResult') }}</p>
        </div>
        <div class="teacher-quiz-detail__results-stat">
          <p class="teacher-quiz-detail__results-stat-value" dir="ltr">{{ completionRate }}%</p>
          <p class="teacher-quiz-detail__results-stat-label">{{ $t('teacher.quizzes.completionRate') }}</p>
        </div>
      </div>

      <div v-if="latestAttempts.length" class="teacher-quiz-detail__attempts">
        <p class="teacher-quiz-detail__section-sub mb-2">{{ $t('teacher.quizzes.recentAttempts') }}</p>
        <div v-for="attempt in latestAttempts" :key="attempt.id" class="teacher-quiz-detail__attempt-row">
          <div class="min-width-0">
            <p class="teacher-quiz-detail__attempt-name">{{ attempt.student_name }}</p>
            <p class="teacher-quiz-detail__attempt-meta">{{ formatDate(attempt.submitted_at) }}</p>
          </div>
          <span class="teacher-quiz-detail__attempt-score" dir="ltr">{{ formatPercent(attempt.percent) }}</span>
        </div>
      </div>

      <p v-else class="teacher-quiz-detail__section-sub mb-3">{{ $t('teacher.quizzes.noAttempts') }}</p>

      <v-btn variant="tonal" rounded="lg" block :to="resultsTo">
        {{ $t('teacher.actions.viewAllResults') }}
        <v-icon end size="16">mdi-arrow-left</v-icon>
      </v-btn>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  analytics: { type: Object, default: null },
  attempts: { type: Array, default: () => [] },
  courseId: { type: [Number, String], required: true },
  quizId: { type: [Number, String], required: true },
})

const averageScore = computed(() => props.analytics?.average_score)
const highestScore = computed(() => props.analytics?.highest_score)
const lowestScore = computed(() => props.analytics?.lowest_score)
const completionRate = computed(() => props.analytics?.completion_rate ?? 0)

const latestAttempts = computed(() => {
  const sorted = [...props.attempts]
    .filter((a) => a.submitted_at)
    .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))
  return sorted.slice(0, 5)
})

const resultsTo = computed(() => ({
  name: 'teacher-quiz-results',
  params: { courseId: props.courseId, quizId: props.quizId },
}))

function formatPercent(value) {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  return `${n % 1 === 0 ? n : n.toFixed(1)}%`
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ar-SY', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<style scoped>
.min-width-0 {
  min-width: 0;
}
</style>
