<template>
  <v-card
    class="glass-card glass-card--elevated pa-5 mb-6 reports-card"
    variant="flat"
    :to="ROUTES.PARENT_REPORTS"
    hover
  >
    <div class="d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="primary">mdi-file-chart-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.reports.summary.title') }}</h3>
      </div>
      <v-chip size="x-small" variant="tonal" append-icon="mdi-chevron-left">{{ t('parent.reports.summary.openCenter') }}</v-chip>
    </div>
    <p v-if="summary" class="text-body-2 mb-2">{{ summary }}</p>
    <div v-if="comparison" class="d-flex flex-wrap gap-3">
      <v-chip v-if="comparison.study" size="small" variant="tonal" color="secondary">
        {{ t('parent.reports.summary.studyTime', { value: comparison.study }) }}
      </v-chip>
      <v-chip v-if="comparison.grades" size="small" variant="tonal" color="success">
        {{ t('parent.reports.summary.average', { value: comparison.grades }) }}
      </v-chip>
    </div>
    <p v-else class="text-caption text-medium-emphasis mb-0">
      {{ t('parent.reports.summary.hint') }}
    </p>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

defineProps({
  summary: { type: String, default: '' },
  comparison: { type: Object, default: null },
})

const { t } = useI18n()
</script>

<style scoped>
.reports-card {
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(34, 211, 238, 0.15);
}
</style>
