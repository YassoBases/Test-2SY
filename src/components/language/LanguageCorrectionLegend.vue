<template>
  <div v-if="grammar || pronunciation" class="d-flex flex-wrap align-center gap-3 mt-1" dir="ltr">
    <span v-if="grammar" class="legend-item"><span class="dot grammar" /> grammar</span>
    <span v-if="pronunciation" class="legend-item"><span class="dot pron" /> pronunciation</span>
    <span class="legend-item"><span class="dot fix" /> correction</span>
  </div>
</template>

<script setup>
// Shared colour key for corrections everywhere: grammar = red, pronunciation/dialect = yellow,
// the fix = green. Keeps the scheme consistent across every feature.
defineProps({
  grammar: { type: Boolean, default: true },
  pronunciation: { type: Boolean, default: false },
})
</script>

<style scoped>
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.7;
}
.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
}
.dot.grammar { background: rgb(var(--v-theme-error)); }
.dot.pron { background: rgb(var(--v-theme-warning)); }
.dot.fix { background: rgb(var(--v-theme-success)); }
</style>
