<template>
  <v-card v-if="evaluation" class="evaluation-card glass-card pa-3 mb-3" variant="flat">
    <div class="d-flex align-center justify-space-between mb-2 flex-wrap gap-2">
      <span class="text-caption font-weight-bold text-medium-emphasis">Tour analysis</span>
      <v-chip v-if="evaluation.estimated_cefr" size="x-small" color="secondary" variant="flat">
        {{ evaluation.estimated_cefr }}
      </v-chip>
    </div>

    <v-row dense class="mb-2">
      <v-col v-for="item in scoreItems" :key="item.key" cols="6" sm="3">
        <div class="score-pill text-center pa-2 rounded-lg">
          <div class="text-caption text-medium-emphasis">{{ item.label }}</div>
          <div class="text-body-1 font-weight-bold">{{ item.value }}</div>
        </div>
      </v-col>
    </v-row>

    <div v-if="pronunciation" class="pron-block rounded-lg pa-2 mb-2" dir="ltr">
      <div class="d-flex align-center justify-space-between mb-1">
        <span class="text-caption font-weight-bold text-medium-emphasis">Pronunciation</span>
        <v-chip size="x-small" :color="pronColor" variant="flat">{{ pronunciation.overall_score }}/100</v-chip>
      </div>
      <div v-if="weakWords.length" class="d-flex flex-wrap gap-1 mb-1">
        <v-chip
          v-for="w in weakWords"
          :key="w.word"
          size="x-small"
          color="warning"
          variant="tonal"
          :title="w.issue || 'needs practice'"
        >
          {{ w.word }}<span v-if="w.issue" class="text-disabled ml-1">· {{ w.issue }}</span>
        </v-chip>
      </div>
      <p v-if="pronunciation.note" class="text-caption mb-0">{{ pronunciation.note }}</p>
    </div>

    <p v-if="evaluation.coaching_note_ar" class="text-caption mb-0">{{ evaluation.coaching_note_ar }}</p>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  evaluation: { type: Object, default: null },
})

const scoreItems = computed(() => {
  const s = props.evaluation?.scores || {}
  return [
    { key: 'fluency', label: 'fluency', value: s.fluency ?? 0 },
    { key: 'grammar', label: 'rules', value: s.grammar ?? 0 },
    { key: 'vocabulary', label: 'Vocabulary', value: s.vocabulary ?? 0 },
    { key: 'confidence', label: 'trust', value: s.confidence ?? 0 },
  ]
})

const pronunciation = computed(() => props.evaluation?.pronunciation || null)
const weakWords = computed(() =>
  (pronunciation.value?.words || []).filter((w) => w.weak),
)
const pronColor = computed(() => {
  const s = pronunciation.value?.overall_score ?? 0
  if (s >= 85) return 'success'
  if (s >= 70) return 'secondary'
  return 'warning'
})
</script>

<style scoped>
.score-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.pron-block {
  background: rgba(var(--v-theme-warning), 0.06);
  border: 1px solid rgba(var(--v-theme-warning), 0.18);
}
</style>
