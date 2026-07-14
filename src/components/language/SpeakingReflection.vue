<template>
  <section v-if="visible" class="reflection glass-card pa-5 pa-md-6 mb-5" role="status">
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon color="success" aria-hidden="true">mdi-check-decagram-outline</v-icon>
      <div class="text-subtitle-1 font-weight-bold mb-0">
        {{ t('student.languages.speakingJourney.reflection.title') }}
      </div>
    </div>

    <p v-if="summary" class="text-body-1 mb-4">{{ summary }}</p>

    <v-row dense>
      <v-col v-if="improvingSkills.length" cols="12" md="6">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.reflection.improved') }}
        </div>
        <ul class="ref-list">
          <li v-for="(s, i) in improvingSkills.slice(0, 3)" :key="`imp-${i}`">
            <strong>{{ s.label }}</strong>
            <span v-if="s.improvement_focus" class="text-medium-emphasis"> — {{ s.improvement_focus }}</span>
          </li>
        </ul>
      </v-col>
      <v-col v-if="practiceSkills.length" cols="12" md="6">
        <div class="text-caption text-medium-emphasis mb-2">
          {{ t('student.languages.speakingJourney.reflection.needsPractice') }}
        </div>
        <ul class="ref-list">
          <li v-for="(s, i) in practiceSkills.slice(0, 3)" :key="`prac-${i}`">
            <strong>{{ s.label }}</strong>
            <span v-if="s.improvement_focus" class="text-medium-emphasis"> — {{ s.improvement_focus }}</span>
          </li>
        </ul>
      </v-col>
    </v-row>

    <div v-if="nextMission" class="next-box rounded-lg pa-4 mt-4">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.reflection.nextLesson') }}
      </div>
      <div class="text-body-1 font-weight-medium">{{ nextMission.title }}</div>
      <div class="text-body-2 text-medium-emphasis">{{ nextMission.purpose }}</div>
    </div>

    <v-chip
      v-if="sessionOutcome?.retry_same_target"
      class="mt-4"
      size="small"
      color="warning"
      variant="tonal"
    >
      {{ t('student.languages.speakingJourney.reflection.retryHint') }}
    </v-chip>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  sessionOutcome: { type: Object, default: null },
  improvingSkills: { type: Array, default: () => [] },
  weakSkills: { type: Array, default: () => [] },
  retentionNeeded: { type: Array, default: () => [] },
  nextMission: { type: Object, default: null },
})

const { t } = useI18n()

const visible = computed(
  () => Boolean(props.sessionOutcome?.student_summary) || Boolean(props.sessionOutcome?.outcome_kind),
)
const summary = computed(() => props.sessionOutcome?.student_summary || '')
const practiceSkills = computed(() => {
  if (props.weakSkills?.length) return props.weakSkills
  return props.retentionNeeded || []
})
</script>

<style scoped>
.reflection {
  border-radius: var(--em-radius-md, 16px);
}
.ref-list {
  margin: 0;
  padding-inline-start: 1.1rem;
}
.next-box {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
</style>
