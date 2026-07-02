<template>
  <v-card v-if="insight" class="glass-card pa-5 mb-4" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <h3 class="text-h6 font-weight-bold mb-0">{{ $t('teacher.students.insightTitle') }}</h3>
      <v-chip v-if="insight.scope_subjects?.length" size="small" variant="tonal" color="primary">
        {{ insight.scope_subjects.join(' · ') }}
      </v-chip>
    </div>

    <v-row dense>
      <v-col cols="12" md="6">
        <div class="text-subtitle-2 font-weight-bold text-success mb-2">{{ $t('teacher.students.strengths') }}</div>
        <ul class="insight-list insight-list--strengths">
          <li v-for="(item, i) in insight.strengths" :key="`s-${i}`">{{ item }}</li>
        </ul>
      </v-col>
      <v-col cols="12" md="6">
        <div class="text-subtitle-2 font-weight-bold text-warning mb-2">{{ $t('teacher.students.needsImprovement') }}</div>
        <ul class="insight-list insight-list--improve">
          <li v-for="(item, i) in insight.improvements" :key="`i-${i}`">{{ item }}</li>
        </ul>
      </v-col>
    </v-row>

    <v-divider class="my-4 border-opacity-25" />

    <v-row dense class="mb-3">
      <v-col cols="12" sm="6">
        <div class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.students.lastActivityInSubject') }}</div>
        <div class="text-body-2 font-weight-medium">{{ insight.last_activity_title || '—' }}</div>
        <div v-if="insight.last_activity_at" class="text-caption">{{ formatDate(insight.last_activity_at) }}</div>
      </v-col>
      <v-col cols="12" sm="6">
        <div class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.students.lastQuizResult') }}</div>
        <div class="text-body-2 font-weight-medium">
          <template v-if="insight.last_quiz_title">
            {{ insight.last_quiz_title }}
            <v-chip
              v-if="insight.last_quiz_score_percent != null"
              size="x-small"
              variant="tonal"
              :color="insight.last_quiz_score_percent >= 60 ? 'success' : 'warning'"
              class="ms-1"
            >
              {{ insight.last_quiz_score_percent }}%
            </v-chip>
          </template>
          <template v-else>—</template>
        </div>
        <div v-if="insight.last_quiz_at" class="text-caption">{{ formatDate(insight.last_quiz_at) }}</div>
      </v-col>
    </v-row>

    <div v-if="insight.suggested_actions?.length">
      <div class="text-subtitle-2 font-weight-bold mb-2">{{ $t('teacher.students.suggestedActions') }}</div>
      <v-chip
        v-for="(action, i) in insight.suggested_actions"
        :key="`a-${i}`"
        size="small"
        variant="tonal"
        class="me-1 mb-1"
      >
        {{ action }}
      </v-chip>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  insight: { type: Object, default: null },
})

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>

<style scoped>
.insight-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.insight-list li {
  position: relative;
  padding-right: 1.25rem;
  margin-bottom: 0.35rem;
  font-size: 0.875rem;
}
.insight-list--strengths li::before {
  content: '✓';
  position: absolute;
  right: 0;
  color: rgb(var(--v-theme-success));
}
.insight-list--improve li::before {
  content: '•';
  position: absolute;
  right: 0;
  color: rgb(var(--v-theme-warning));
}
</style>
