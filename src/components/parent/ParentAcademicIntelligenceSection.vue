<template>
  <v-card class="glass-card pa-5 mb-6 academic-intel" variant="flat">
    <div class="d-flex align-center flex-wrap gap-2 mb-4">
      <v-icon color="secondary">mdi-school-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.performance.academicIntel.title') }}</h3>
      <v-chip size="x-small" variant="tonal" class="ms-auto">{{ t('parent.performance.academicIntel.fromRealData') }}</v-chip>
    </div>

    <v-alert
      v-if="!data?.has_data"
      type="info"
      variant="tonal"
      density="comfortable"
      class="rounded-lg mb-0"
    >
      {{ data?.summary || t('parent.performance.academicIntel.noData') }}
    </v-alert>

    <template v-else>
      <p class="text-body-2 text-medium-emphasis mb-4">{{ data.summary }}</p>

      <v-row dense class="mb-4">
        <v-col cols="12" sm="4">
          <div class="metric-card metric-card--primary">
            <div class="metric-card__label">{{ t('parent.performance.academicIntel.overallAverage') }}</div>
            <div class="metric-card__value">{{ formatScore(data.overall_average) }}</div>
            <v-chip
              v-if="data.performance_label"
              size="small"
              :color="indicatorColor(data.performance_indicator)"
              variant="flat"
              class="mt-2"
            >
              {{ data.performance_label }}
            </v-chip>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="metric-card">
            <div class="metric-card__label">{{ t('parent.performance.academicIntel.bestSubject') }}</div>
            <div class="metric-card__subject">{{ data.best_subject?.subject_name || t('parent.common.emDash') }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatScore(data.best_subject?.composite_score) }}
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="metric-card">
            <div class="metric-card__label">{{ t('parent.performance.academicIntel.weakestSubject') }}</div>
            <div class="metric-card__subject">{{ data.weakest_subject?.subject_name || t('parent.common.emDash') }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatScore(data.weakest_subject?.composite_score) }}
            </div>
          </div>
        </v-col>
      </v-row>

      <div class="mb-5">
        <div class="text-subtitle-2 font-weight-bold mb-3">{{ t('parent.performance.academicIntel.subjectComparison') }}</div>
        <div
          v-for="row in data.subject_comparison"
          :key="row.subject_name"
          class="comparison-row mb-3"
        >
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="font-weight-medium">{{ row.subject_name }}</span>
            <span class="text-caption">{{ formatScore(row.composite_score) }}</span>
          </div>
          <v-progress-linear
            :model-value="row.composite_score ?? 0"
            :color="barColor(row.composite_score)"
            height="10"
            rounded
          />
        </div>
      </div>

      <div class="text-subtitle-2 font-weight-bold mb-3">{{ t('parent.performance.academicIntel.subjectAnalysis') }}</div>
      <v-row dense>
        <v-col
          v-for="subject in data.subjects"
          :key="subject.course_id"
          cols="12"
          md="6"
        >
          <div class="subject-card pa-4 rounded-lg h-100">
            <div class="d-flex align-center justify-space-between mb-3">
              <div>
                <div class="font-weight-bold">{{ subject.subject_name }}</div>
                <div class="text-caption text-medium-emphasis">{{ subject.course_title }}</div>
              </div>
              <v-chip
                v-if="subject.performance_label"
                size="x-small"
                :color="indicatorColor(subject.performance_indicator)"
                variant="tonal"
              >
                {{ subject.performance_label }}
              </v-chip>
            </div>

            <div class="subject-metrics">
              <div class="subject-metric">
                <span class="subject-metric__label">{{ t('parent.performance.academicIntel.lessonQuizzes') }}</span>
                <strong>{{ formatScore(subject.quiz_average) }}</strong>
                <span class="text-caption">{{ t('parent.performance.academicIntel.attempts', { n: subject.quiz_attempts }) }}</span>
              </div>
              <div class="subject-metric">
                <span class="subject-metric__label">{{ t('parent.performance.academicIntel.teacherExams') }}</span>
                <strong>{{ formatScore(subject.exam_average) }}</strong>
                <span class="text-caption">{{ t('parent.performance.academicIntel.attempts', { n: subject.exam_attempts }) }}</span>
              </div>
              <div class="subject-metric">
                <span class="subject-metric__label">{{ t('parent.performance.academicIntel.lessonCompletion') }}</span>
                <strong>{{ formatScore(subject.completion_rate) }}</strong>
                <span class="text-caption">
                  {{ t('parent.performance.academicIntel.lessonsRatio', { completed: subject.completed_lessons, total: subject.total_lessons }) }}
                </span>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>

      <div class="data-sources mt-4 text-caption text-medium-emphasis">
        {{ t('parent.performance.academicIntel.dataSources') }}
        {{ t('parent.performance.academicIntel.dataSourcesLine', {
          quizAttempts: data.data_sources?.quiz_attempts ?? 0,
          examAttempts: data.data_sources?.exam_attempts ?? 0,
          completedLessons: data.data_sources?.lesson_completions ?? 0,
        }) }}
        <span v-if="!data.data_sources?.assignments_available">{{ t('parent.performance.academicIntel.assignmentsUnavailable') }}</span>
      </div>
    </template>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  data: { type: Object, default: null },
})

const { t } = useI18n()

const data = computed(() => props.data || {})

function formatScore(value) {
  if (value == null || Number.isNaN(Number(value))) return t('parent.common.emDash')
  return `${Math.round(Number(value))}%`
}

function indicatorColor(indicator) {
  if (indicator === 'excellent') return 'success'
  if (indicator === 'good') return 'info'
  if (indicator === 'needs_improvement') return 'warning'
  return 'default'
}

function barColor(score) {
  if (score == null) return 'grey'
  if (score >= 85) return 'success'
  if (score >= 70) return 'info'
  return 'warning'
}
</script>

<style scoped>
.academic-intel {
  border: 1px solid rgba(124, 108, 240, 0.18);
}

.metric-card {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  min-height: 120px;
}

.metric-card--primary {
  background: rgba(124, 108, 240, 0.08);
  border-color: rgba(124, 108, 240, 0.22);
}

.metric-card__label {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.55);
  margin-bottom: 6px;
}

.metric-card__value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.1;
}

.metric-card__subject {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.subject-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.subject-metrics {
  display: grid;
  gap: 10px;
}

.subject-metric {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.subject-metric__label {
  flex: 1;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.6);
}

.comparison-row {
  padding: 2px 0;
}
</style>
