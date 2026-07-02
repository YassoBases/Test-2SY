<template>
  <div v-if="items.length" dir="ltr">
    <div v-for="(e, i) in items" :key="i" class="text-body-2 mb-1">
      <span :class="e.type === 'pronunciation' ? 'pron-word' : 'wrong-word'">{{ e.original }}</span>
      <span class="mx-1 text-medium-emphasis">→</span>
      <strong class="right-word">{{ e.corrected }}</strong>
      <span v-if="e.explanation" class="text-caption text-medium-emphasis"> — {{ e.explanation }}</span>
    </div>
    <LanguageCorrectionLegend :grammar="hasGrammar" :pronunciation="hasPron" class="mt-2" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LanguageCorrectionLegend from './LanguageCorrectionLegend.vue'

// Renders a list of discrete corrections (exam report, placement recommendation, writing, …) with
// the shared colour scheme: original red (grammar) / yellow (pronunciation), the fix green.
const props = defineProps({
  // [{ original, corrected, type: 'grammar'|'pronunciation', explanation? }]
  errors: { type: Array, default: () => [] },
})

const items = computed(() =>
  (props.errors || [])
    .map((e) => ({
      original: e.original ?? e.original_text ?? '',
      corrected: e.corrected ?? e.corrected_text ?? '',
      type: e.type === 'pronunciation' ? 'pronunciation' : 'grammar',
      explanation: e.explanation ?? e.rule ?? '',
    }))
    .filter((e) => e.original || e.corrected),
)
const hasGrammar = computed(() => items.value.some((e) => e.type === 'grammar'))
const hasPron = computed(() => items.value.some((e) => e.type === 'pronunciation'))
</script>

<style scoped>
.wrong-word {
  color: rgb(var(--v-theme-error));
  text-decoration: line-through;
  font-weight: 600;
}
.pron-word {
  color: rgb(var(--v-theme-warning));
  text-decoration: underline dotted;
  font-weight: 600;
}
.right-word {
  color: rgb(var(--v-theme-success));
  font-weight: 700;
}
</style>
