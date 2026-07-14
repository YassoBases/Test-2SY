<template>
  <v-card v-if="hasEvaluation" class="evaluation-panel pa-6 mb-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="secondary" size="28">mdi-clipboard-check-outline</v-icon>
      <div>
        <div class="text-overline text-medium-emphasis">{{ t('student.languages.writingJourney.evaluation.eyebrow') }}</div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.languages.writingJourney.evaluation.title') }}</h3>
      </div>
    </div>

    <div class="mb-5">
      <div class="text-body-2 font-weight-bold mb-3">{{ t('student.languages.writingJourney.evaluation.dimensions') }}</div>
      <v-row dense>
        <v-col v-for="dim in dimensions" :key="dim.key" cols="12" sm="6" md="4">
          <div class="dimension-chip">
            <span class="text-body-2 font-weight-medium">{{ dim.label }}</span>
            <v-chip
              :color="dim.status === 'on_track' ? 'success' : 'warning'"
              variant="tonal"
              size="small"
              class="ms-auto"
            >
              {{ t(`student.languages.writingJourney.evaluation.status.${dim.status}`) }}
            </v-chip>
          </div>
        </v-col>
      </v-row>
    </div>

    <div v-if="successCriteria.length" class="mb-5">
      <div class="text-body-2 font-weight-bold mb-3">{{ t('student.languages.writingJourney.evaluation.criteriaTitle') }}</div>
      <div v-for="(item, idx) in successCriteria" :key="idx" class="criterion-row">
        <v-icon
          :color="criterionColor(displayStatus(item))"
          size="20"
          class="me-2 mt-1"
        >
          {{ criterionIcon(displayStatus(item)) }}
        </v-icon>
        <div>
          <span class="text-body-2" dir="ltr">{{ item.label }}</span>
          <div class="text-caption" :class="`text-${criterionColor(displayStatus(item))}`">
            {{ t(`student.languages.writingJourney.evaluation.criteriaStatus.${displayStatus(item)}`) }}
          </div>
        </div>
      </div>
    </div>

    <v-row>
      <v-col v-if="strengths.length" cols="12" md="6">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.evaluation.strengths') }}</div>
        <div v-for="(line, idx) in strengths" :key="`s-${idx}`" class="d-flex align-start gap-2 py-1">
          <v-icon color="success" size="18" class="mt-1">mdi-check</v-icon>
          <span class="text-body-2" dir="ltr">{{ line }}</span>
        </div>
      </v-col>
      <v-col v-if="improvements.length" cols="12" md="6">
        <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.evaluation.improve') }}</div>
        <div v-for="(line, idx) in improvements" :key="`i-${idx}`" class="d-flex align-start gap-2 py-1">
          <v-icon color="warning" size="18" class="mt-1">mdi-circle-small</v-icon>
          <span class="text-body-2" dir="ltr">{{ line }}</span>
        </div>
      </v-col>
    </v-row>

    <v-alert
      v-if="readyToComplete"
      type="success"
      variant="tonal"
      density="comfortable"
      class="mt-4 rounded-lg"
    >
      {{ t('student.languages.writingJourney.evaluation.readyBanner') }}
    </v-alert>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  hasEvaluation: { type: Boolean, default: false },
  dimensions: { type: Array, default: () => [] },
  successCriteria: { type: Array, default: () => [] },
  strengths: { type: Array, default: () => [] },
  improvements: { type: Array, default: () => [] },
  readyToComplete: { type: Boolean, default: false },
})

const { t } = useI18n()

// Prefer the 4-state display status; fall back to the legacy 3-state status.
function displayStatus(item) {
  if (item.display_status) return item.display_status
  if (item.status === 'met') return 'met'
  if (item.status === 'partial') return 'partially_met'
  return 'not_attempted'
}

function criterionIcon(status) {
  if (status === 'met') return 'mdi-check-circle'
  if (status === 'partially_met') return 'mdi-circle-half-full'
  if (status === 'attempted_inaccurately') return 'mdi-alert-circle-outline'
  return 'mdi-close-circle-outline'
}

function criterionColor(status) {
  if (status === 'met') return 'success'
  if (status === 'partially_met') return 'warning'
  if (status === 'attempted_inaccurately') return 'warning'
  return 'error'
}
</script>

<style scoped>
.evaluation-panel {
  border-radius: 20px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.12);
}
.dimension-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.04);
  min-height: 100%;
}
.criterion-row {
  display: flex;
  align-items: flex-start;
  padding: 0.35rem 0;
}
</style>
