<template>
  <v-card class="unlock-card pa-6 mb-4" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-2">{{ headline }}</h3>
    <p v-if="summary" class="text-body-2 text-medium-emphasis mb-4">{{ summary }}</p>

    <div v-if="checklist.length" class="unlock-checklist">
      <div
        v-for="(item, idx) in checklist"
        :key="idx"
        class="unlock-check-item d-flex align-start gap-3 py-2"
      >
        <v-icon color="medium-emphasis" size="22" class="flex-shrink-0 mt-1">
          mdi-checkbox-blank-circle-outline
        </v-icon>
        <span class="text-body-1">{{ item }}</span>
      </div>
    </div>

    <p v-if="nextStep" class="text-body-2 font-weight-medium mt-4 mb-0 next-step">
      <v-icon size="18" color="secondary" class="me-1">mdi-arrow-right-circle-outline</v-icon>
      {{ nextStep }}
    </p>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  journey: { type: Object, default: null },
  canStartTest: { type: Boolean, default: false },
})

const { t } = useI18n()

const narrative = computed(() => props.journey?.narrative || {})

const headline = computed(() =>
  props.canStartTest
    ? t('student.languages.coach.promotion.unlockedTitle')
    : t('student.languages.coach.promotion.blockedTitle'),
)

const summary = computed(() => {
  if (props.canStartTest) return t('student.languages.coach.promotion.unlockedBody')
  return narrative.value.promotion_progress_message || ''
})

const checklist = computed(() => narrative.value.unlock_checklist || [])

const nextStep = computed(() => {
  if (props.canStartTest) return t('student.languages.coach.promotion.nextStartTest')
  const events = narrative.value.history_events || []
  return events[0]?.text || t('student.languages.coach.promotion.nextPractice')
})
</script>

<style scoped>
.unlock-card {
  border-radius: 20px;
  background: rgba(var(--v-theme-surface), 1);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.unlock-check-item + .unlock-check-item {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.next-step {
  color: rgb(var(--v-theme-secondary));
}
</style>
