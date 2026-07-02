<template>
  <v-card
    v-if="insight || summaryLine"
    class="glass-card glass-card--elevated pa-5 mb-6 ai-insight-card"
    variant="flat"
    :to="ROUTES.PARENT_INSIGHTS"
    hover
  >
    <div class="d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-robot-happy-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.insights.latestInsight') }}</h3>
      </div>
      <v-chip size="x-small" variant="tonal" append-icon="mdi-chevron-left">{{ t('parent.insights.viewAnalysis') }}</v-chip>
    </div>

    <v-skeleton-loader v-if="loading" type="text@2" />

    <template v-else>
      <p v-if="insight" class="text-body-1 font-weight-medium mb-2">{{ insight.text }}</p>
      <p v-if="summaryLine" class="text-caption text-medium-emphasis mb-0">{{ summaryLine }}</p>
    </template>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

defineProps({
  insight: { type: Object, default: null },
  summaryLine: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const { t } = useI18n()
</script>

<style scoped>
.ai-insight-card {
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(124, 108, 240, 0.2);
  transition: border-color 0.2s ease;
}
.ai-insight-card:hover {
  border-color: rgba(124, 108, 240, 0.45);
}
</style>
