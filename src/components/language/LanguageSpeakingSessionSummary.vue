<template>
  <div class="speaking-session-summaries">
    <v-card
      v-for="(item, index) in displaySummaries"
      :key="`summary-${index}`"
      class="glass-card pa-5 speaking-session-summary mb-4"
      variant="flat"
    >
      <div class="text-h6 mb-3">
        {{ displaySummaries.length > 1 ? t('student.languages.speaking.live.summary.turnTitle', { n: index + 1 }) : t('student.languages.speaking.live.summary.title') }}
      </div>

      <p v-if="item.coach_summary" class="text-body-1 mb-4">{{ item.coach_summary }}</p>

      <div v-if="item.strengths?.length" class="mb-4">
        <div class="text-subtitle-2 mb-2">{{ t('student.languages.speaking.live.summary.wentWell') }}</div>
        <ul class="summary-list">
          <li v-for="(s, idx) in item.strengths" :key="`s-${index}-${idx}`">{{ s }}</li>
        </ul>
      </div>

      <div v-if="item.improvements?.length || item.priority_issue" class="mb-4">
        <div class="text-subtitle-2 mb-2">{{ t('student.languages.speaking.live.summary.toImprove') }}</div>
        <ul class="summary-list">
          <li v-if="item.priority_issue">{{ item.priority_issue }}</li>
          <li v-for="(imp, idx) in item.improvements" :key="`i-${index}-${idx}`">{{ imp }}</li>
        </ul>
      </div>

      <div v-if="observationDimensions(item).length" class="mb-4">
        <div class="text-subtitle-2 mb-2">{{ t('student.languages.speaking.live.summary.observations') }}</div>
        <div
          v-for="dim in observationDimensions(item)"
          :key="`${index}-${dim.key}`"
          class="summary-dimension mb-2"
        >
          <div class="d-flex align-center gap-2 flex-wrap">
            <v-chip size="small" variant="tonal" :color="dim.status === 'on_track' ? 'success' : 'warning'">
              {{ dim.label }}
            </v-chip>
            <span class="text-caption">{{ statusLabel(dim.status) }}</span>
          </div>
          <p v-if="dim.reason" class="text-body-2 mt-1 mb-0" dir="ltr">{{ dim.reason }}</p>
        </div>
      </div>

      <div v-if="item.focus_label" class="mb-2">
        <div class="text-subtitle-2 mb-1">{{ t('student.languages.speaking.live.summary.adaptsNext') }}</div>
        <p class="text-body-2 mb-0">{{ item.focus_label }}</p>
      </div>

      <p v-if="item.since_last_time" class="text-body-2 text-medium-emphasis mt-3" dir="ltr">
        {{ item.since_last_time }}
      </p>
    </v-card>

    <v-card v-if="!displaySummaries.length" class="glass-card pa-5 speaking-session-summary" variant="flat">
      <div class="text-h6 mb-2">{{ t('student.languages.speaking.live.summary.completeTitle') }}</div>
      <p class="text-body-2 mb-0">{{ t('student.languages.speaking.live.summary.completeBody') }}</p>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  summary: { type: Object, default: null },
  summaries: { type: Array, default: () => [] },
  showAll: { type: Boolean, default: false },
})

const { t } = useI18n()

const displaySummaries = computed(() => {
  if (props.showAll && props.summaries?.length) return props.summaries
  const one = props.summary || props.summaries?.[props.summaries.length - 1]
  return one ? [one] : []
})

function observationDimensions(item) {
  const dims = item?.dimensions || []
  return dims.filter((d) => d?.reason || d?.status === 'needs_work').slice(0, 4)
}

function statusLabel(status) {
  if (status === 'on_track') return t('student.languages.speaking.live.summary.statusOnTrack')
  return t('student.languages.speaking.live.summary.statusNeedsWork')
}
</script>

<style scoped>
.summary-list {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.summary-dimension {
  border-inline-start: 3px solid rgba(var(--v-theme-secondary), 0.35);
  padding-inline-start: 0.75rem;
}
</style>
