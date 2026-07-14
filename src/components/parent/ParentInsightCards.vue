<template>
  <v-row>
    <v-col
      v-for="insight in insights"
      :key="insight.id"
      cols="12"
      md="6"
    >
      <v-card class="insight-card glass-card pa-4" variant="flat" :class="`insight-card--${insight.severity}`">
        <div class="d-flex align-start gap-3">
          <v-avatar :color="severityColor(insight.severity)" size="40" variant="tonal">
            <v-icon>{{ insight.icon || 'mdi-lightbulb-on' }}</v-icon>
          </v-avatar>
          <div>
            <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.insights.smartRecommendation') }}</p>
            <p class="text-body-2 font-weight-medium mb-1">{{ insight.text }}</p>
            <ul v-if="insight.evidence?.length" class="evidence-list text-caption mb-0">
              <li v-for="(item, idx) in insight.evidence.filter(Boolean)" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  insights: { type: Array, default: () => [] },
})

const { t } = useI18n()

function severityColor(severity) {
  const map = { success: 'success', warning: 'warning', error: 'error', info: 'info' }
  return map[severity] || 'info'
}
</script>

<style scoped>
.insight-card--warning {
  border-inline-start: 3px solid rgb(var(--v-theme-warning));
}

.insight-card--success {
  border-inline-start: 3px solid rgb(var(--v-theme-success));
}

.insight-card--info {
  border-inline-start: 3px solid rgb(var(--v-theme-info));
}

.evidence-list {
  padding-inline-start: 1rem;
  opacity: 0.8;
  line-height: 1.6;
}
</style>
