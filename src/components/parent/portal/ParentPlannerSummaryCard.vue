<template>
  <v-card
    v-if="planner?.commitment"
    class="glass-card glass-card--elevated pa-5 mb-6 planner-summary-card"
    variant="flat"
    :to="ROUTES.PARENT_PLANNER"
    hover
  >
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-calendar-star</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.planner.summary.title') }}</h3>
      </div>
      <v-chip size="x-small" variant="tonal" append-icon="mdi-chevron-left">{{ t('parent.planner.summary.viewDetails') }}</v-chip>
    </div>

    <v-row dense>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold eduspark-gradient-text">
            {{ planner.commitment.adherence_rate }}%
          </div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.planner.summary.planAdherence') }}</div>
        </div>
      </v-col>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold text-warning">
            {{ planner.commitment.pending_count }}
          </div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.planner.summary.pendingTasks') }}</div>
        </div>
      </v-col>
      <v-col cols="4">
        <div class="stat-pill text-center pa-3 rounded-lg">
          <div class="text-h6 font-weight-bold text-error">
            {{ planner.commitment.missed_count }}
          </div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.planner.summary.missedTasks') }}</div>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

defineProps({
  planner: { type: Object, default: null },
})

const { t } = useI18n()
</script>

<style scoped>
.planner-summary-card {
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(124, 108, 240, 0.15);
  transition: border-color 0.2s ease, transform 0.15s ease;
}

.planner-summary-card:hover {
  border-color: rgba(124, 108, 240, 0.4);
  transform: translateY(-2px);
}

.stat-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
