<template>
  <v-card class="glass-card glass-card--elevated pa-4 pa-md-5 section-card" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-clipboard-check-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.performance.quiz.title') }}</h3>
      </div>
      <v-chip size="small" variant="tonal" color="primary">
        {{ t('parent.performance.quiz.average', { score: quiz.average_score ?? 0 }) }}
      </v-chip>
    </div>

    <v-row class="mb-4" dense>
      <v-col v-for="item in quiz.chart" :key="item.subject" cols="6" sm="3">
        <div class="chart-bar text-center pa-3 rounded-lg">
          <div class="bar-track mb-2">
            <div class="bar-fill" :style="{ height: `${item.score}%` }" />
          </div>
          <p class="text-caption font-weight-bold mb-0">{{ item.subject }}</p>
          <p class="text-caption text-medium-emphasis mb-0">{{ item.score }}%</p>
        </div>
      </v-col>
    </v-row>

    <div v-for="q in quiz.recent" :key="q.id" class="quiz-row d-flex align-center gap-3 pa-3 rounded-lg mb-2">
      <v-avatar :color="scoreColor(q.score)" size="40" variant="tonal">
        <span class="text-caption font-weight-bold">{{ q.score }}%</span>
      </v-avatar>
      <div class="flex-grow-1">
        <p class="text-body-2 font-weight-medium mb-0">{{ q.subject }}</p>
        <p class="text-caption text-medium-emphasis mb-0">{{ q.lesson_title || t('parent.performance.quiz.quizFallback', { subject: q.subject }) }}</p>
      </div>
      <div class="text-end">
        <v-chip v-if="q.trend != null" :color="q.trend >= 0 ? 'success' : 'error'" size="x-small" variant="tonal">
          {{ q.trend >= 0 ? '+' : '' }}{{ q.trend }}%
        </v-chip>
        <p class="text-caption text-medium-emphasis mb-0 mt-1">{{ q.relative }}</p>
      </div>
    </div>

    <v-divider class="my-4 border-opacity-25" />

    <div v-for="(comment, i) in quiz.ai_comments" :key="i" class="ai-comment d-flex gap-2 mb-2">
      <v-icon size="16" color="secondary" class="mt-1">mdi-robot</v-icon>
      <p class="text-body-2 mb-0">{{ comment }}</p>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  quiz: {
    type: Object,
    default: () => ({ recent: [], chart: [], ai_comments: [], average_score: 0 }),
  },
})

const { t } = useI18n()

function scoreColor(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}
</script>

<style scoped>
.section-card {
  border-inline-start: 3px solid rgba(34, 211, 238, 0.4);
}

.chart-bar {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chart-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.12);
}

.bar-track {
  height: 56px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, var(--em-cyan), var(--em-purple));
  border-radius: 8px 8px 0 0;
  min-height: 8px;
  transition: height 0.5s ease;
}

.quiz-row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: border-color 0.2s;
}

.quiz-row:hover {
  border-color: rgba(124, 108, 240, 0.35);
}

.ai-comment {
  padding: 8px 12px;
  background: rgba(124, 108, 240, 0.08);
  border-radius: 10px;
}
</style>
