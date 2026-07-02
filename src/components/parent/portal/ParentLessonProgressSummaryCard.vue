<template>
  <v-card
    class="glass-card glass-card--elevated pa-5 mb-6 lessons-card"
    variant="flat"
    :to="ROUTES.PARENT_LESSONS"
    hover
  >
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-book-open-page-variant-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.lessons.summary.title') }}</h3>
      </div>
      <v-chip size="x-small" variant="tonal" append-icon="mdi-chevron-left">{{ t('parent.lessons.summary.viewDetails') }}</v-chip>
    </div>

    <v-row dense>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold text-success">{{ summary.completed_lessons ?? 0 }}</div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.lessons.summary.completed') }}</div>
        </div>
      </v-col>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold text-warning">{{ summary.in_progress_lessons ?? 0 }}</div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.lessons.summary.inProgress') }}</div>
        </div>
      </v-col>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold">{{ summary.pending_lessons ?? 0 }}</div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.lessons.summary.notStarted') }}</div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

defineProps({
  summary: { type: Object, required: true },
})

const { t } = useI18n()
</script>

<style scoped>
.lessons-card {
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(124, 108, 240, 0.15);
}

.stat-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
