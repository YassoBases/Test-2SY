<template>
  <div v-if="display" class="correction-block rounded-lg pa-3 mb-3" dir="ltr">
    <template v-if="display.has_errors || hasWeak">
      <div class="mb-2">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Your sentence:</div>
        <div class="text-body-2">
          <template v-for="(t, i) in diff.orig" :key="`o${i}`"><span :class="origClass(t)">{{ t.text }}</span>{{ i < diff.orig.length - 1 ? ' ' : '' }}</template>
        </div>
      </div>
      <div v-if="display.has_errors" class="mb-2">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Corrected sentence:</div>
        <div class="text-body-2 font-weight-medium">
          <template v-for="(t, i) in diff.corr" :key="`c${i}`"><span :class="t.type === 'added' ? 'right-word' : ''">{{ t.text }}</span>{{ i < diff.corr.length - 1 ? ' ' : '' }}</template>
        </div>
      </div>
      <div v-if="display.explanation" class="mb-2">
        <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Explanation:</div>
        <div class="text-body-2">{{ display.explanation }}</div>
      </div>
      <LanguageCorrectionLegend :grammar="display.has_errors" :pronunciation="hasWeak" />
    </template>
    <p v-else class="text-body-2 font-weight-medium text-success mb-0">
      {{ display.no_correction_message || 'Excellent. No correction needed.' }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LanguageCorrectionLegend from './LanguageCorrectionLegend.vue'

const props = defineProps({
  display: { type: Object, default: null },
  // Mispronounced words (pronunciation/dialect slips) — shown yellow even when spelled correctly.
  weakWords: { type: Array, default: () => [] },
})

const norm = (w) => (w || '').toLowerCase().replace(/[.,!?;:'"]/g, '')

const weakSet = computed(() => {
  const out = new Set()
  // From an explicit prop or carried on the correction payload itself (display.weak_words).
  for (const list of [props.weakWords || [], props.display?.weak_words || []]) {
    for (const w of list) {
      const word = typeof w === 'string' ? w : w?.word
      if (word) out.add(norm(word))
    }
  }
  return out
})
const hasWeak = computed(() => weakSet.value.size > 0)

function origClass(t) {
  if (t.type === 'removed') return 'wrong-word' // grammar -> red
  if (t.type === 'same' && weakSet.value.has(norm(t.text))) return 'pron-word' // pronunciation -> yellow
  return ''
}

/** LCS word diff: tag original tokens removed/same and corrected tokens added/same. */
function lcsWordDiff(a, b) {
  const aw = (a || '').trim().split(/\s+/).filter(Boolean)
  const bw = (b || '').trim().split(/\s+/).filter(Boolean)
  const n = aw.length
  const m = bw.length
  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0))
  for (let i = n - 1; i >= 0; i -= 1) {
    for (let j = m - 1; j >= 0; j -= 1) {
      dp[i][j] = norm(aw[i]) === norm(bw[j])
        ? dp[i + 1][j + 1] + 1
        : Math.max(dp[i + 1][j], dp[i][j + 1])
    }
  }
  const orig = []
  const corr = []
  let i = 0
  let j = 0
  while (i < n && j < m) {
    if (norm(aw[i]) === norm(bw[j])) {
      orig.push({ text: aw[i], type: 'same' })
      corr.push({ text: bw[j], type: 'same' })
      i += 1
      j += 1
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      orig.push({ text: aw[i], type: 'removed' })
      i += 1
    } else {
      corr.push({ text: bw[j], type: 'added' })
      j += 1
    }
  }
  while (i < n) { orig.push({ text: aw[i], type: 'removed' }); i += 1 }
  while (j < m) { corr.push({ text: bw[j], type: 'added' }); j += 1 }
  return { orig, corr }
}

const diff = computed(() =>
  lcsWordDiff(props.display?.your_sentence, props.display?.corrected_sentence),
)
</script>

<style scoped>
.correction-block {
  background: rgba(var(--v-theme-info), 0.08);
  border: 1px solid rgba(var(--v-theme-info), 0.2);
}
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
