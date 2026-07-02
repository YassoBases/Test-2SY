<template>
  <v-card class="glass-card glass-card--solid pa-4" variant="flat">
    <div v-if="subjects.length" class="d-flex flex-column gap-2">
      <div
        v-for="subj in subjects"
        :key="subj.subject_name"
        class="subject-row d-flex align-center gap-3 pa-3 rounded-lg"
      >
        <div class="flex-grow-1 min-w-0">
          <div class="text-body-2 font-weight-medium">{{ subj.subject_name }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ t('common.planner.subjectStats', { completion: subj.completion_percent, average: subj.average_score }) }}
            <span v-if="subj.missed_lessons">{{ t('common.planner.missedLessons', { count: subj.missed_lessons }) }}</span>
          </div>
        </div>
        <v-chip size="small" :color="strengthColor(subj.strength_level)" variant="tonal">
          {{ subj.strength_label }}
        </v-chip>
      </div>
    </div>
    <p v-else class="text-body-2 text-medium-emphasis mb-0 text-center py-4">
      {{ t('common.planner.subjectAnalysisEmpty') }}
    </p>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  subjects: { type: Array, default: () => [] },
})

const { t } = useI18n()

function strengthColor(level) {
  return { weak: 'error', medium: 'warning', strong: 'success' }[level] || 'grey'
}
</script>

<style scoped>
.subject-row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(124, 108, 240, 0.12);
}
</style>
