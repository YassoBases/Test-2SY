<template>
  <v-card v-if="alerts.length" class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="error">mdi-shield-alert-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.insights.riskAlerts.title') }}</h3>
    </div>
    <v-alert
      v-for="alert in alerts"
      :key="alert.id"
      :type="alert.severity === 'error' ? 'error' : 'warning'"
      variant="tonal"
      density="comfortable"
      class="mb-2 rounded-lg"
    >
      <div class="font-weight-medium">{{ alert.text }}</div>
      <ul v-if="alert.evidence?.length" class="evidence-list text-caption mt-2 mb-0">
        <li v-for="(item, idx) in alert.evidence" :key="idx">{{ item }}</li>
      </ul>
      <p v-if="alert.data_source" class="text-caption text-medium-emphasis mb-0 mt-1">
        {{ t('parent.insights.riskAlerts.source', { source: sourceLabel(alert.data_source) }) }}
      </p>
    </v-alert>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  alerts: { type: Array, default: () => [] },
})

const { t } = useI18n()

function sourceLabel(key) {
  const path = `parent.insights.riskAlerts.sources.${key}`
  const translated = t(path)
  return translated !== path ? translated : key
}
</script>

<style scoped>
.evidence-list {
  padding-inline-start: 1rem;
  opacity: 0.85;
}
</style>
