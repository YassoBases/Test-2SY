<template>
  <v-card class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="info">mdi-brain</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.insights.studyBehavior.title') }}</h3>
    </div>

    <v-row v-if="behavior" dense>
      <v-col cols="6" sm="3">
        <div class="metric pa-3 rounded-lg text-center">
          <div class="text-h6 font-weight-bold">{{ behavior.average_daily_study_hours }}</div>
          <p class="text-caption mb-0">{{ t('parent.insights.studyBehavior.dailyHours') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric pa-3 rounded-lg text-center">
          <div class="text-body-1 font-weight-bold text-truncate">
            {{ behavior.preferred_study_hours_label || t('parent.common.emDash') }}
          </div>
          <p class="text-caption mb-0">{{ t('parent.insights.studyBehavior.preferredTime') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric pa-3 rounded-lg text-center">
          <v-chip
            size="small"
            :color="consistencyColor"
            variant="tonal"
          >
            {{ behavior.consistency_label || t('parent.common.emDash') }}
          </v-chip>
          <p class="text-caption mb-0 mt-2">{{ t('parent.insights.studyBehavior.consistency') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric pa-3 rounded-lg text-center">
          <div class="text-h6 font-weight-bold">
            {{ behavior.active_days_this_week }}/{{ behavior.total_days_this_week }}
          </div>
          <p class="text-caption mb-0">{{ t('parent.insights.studyBehavior.activeDays') }}</p>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  behavior: { type: Object, default: null },
})

const { t } = useI18n()

const consistencyColor = computed(() => {
  const level = props.behavior?.consistency_level
  if (level === 'high') return 'success'
  if (level === 'medium') return 'info'
  if (level === 'low') return 'warning'
  return 'grey'
})
</script>

<style scoped>
.metric {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  min-height: 72px;
}
</style>
