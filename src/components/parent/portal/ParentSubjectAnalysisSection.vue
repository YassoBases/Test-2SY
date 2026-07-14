<template>
  <v-row class="mb-6">
    <v-col cols="12" md="6">
      <v-card class="glass-card pa-4 h-100 subject-card subject-card--strength" variant="flat">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon color="success">mdi-trophy-outline</v-icon>
          <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.insights.subjectAnalysis.strongest') }}</h3>
        </div>
        <template v-if="strength?.subject">
          <p class="text-h5 font-weight-bold mb-3">{{ strength.subject }}</p>
          <ul class="reason-list mb-0">
            <li v-for="(reason, idx) in strength.reasons" :key="idx">{{ reason }}</li>
          </ul>
          <div v-if="strength.average_score != null" class="mt-3">
            <v-chip size="small" color="success" variant="tonal">
              {{ t('parent.insights.subjectAnalysis.average', { score: strength.average_score }) }}
            </v-chip>
          </div>
        </template>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.insights.subjectAnalysis.noData') }}</p>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="glass-card pa-4 h-100 subject-card subject-card--weakness" variant="flat">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon color="warning">mdi-alert-decagram-outline</v-icon>
          <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.insights.subjectAnalysis.weakest') }}</h3>
        </div>
        <template v-if="weakness?.subject">
          <p class="text-h5 font-weight-bold mb-3">{{ weakness.subject }}</p>
          <ul class="reason-list mb-0">
            <li v-for="(reason, idx) in weakness.reasons" :key="idx">{{ reason }}</li>
          </ul>
          <div v-if="weakness.average_score != null" class="mt-3">
            <v-chip size="small" color="warning" variant="tonal">
              {{ t('parent.insights.subjectAnalysis.average', { score: weakness.average_score }) }}
            </v-chip>
          </div>
        </template>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.insights.subjectAnalysis.noData') }}</p>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  strength: { type: Object, default: null },
  weakness: { type: Object, default: null },
})

const { t } = useI18n()
</script>

<style scoped>
.subject-card {
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.subject-card--strength {
  border-inline-start: 3px solid rgb(var(--v-theme-success));
}
.subject-card--weakness {
  border-inline-start: 3px solid rgb(var(--v-theme-warning));
}
.reason-list {
  padding-inline-start: 1.1rem;
  line-height: 1.8;
}
</style>
