<template>
  <footer class="session-footer">
    <StageProgress
      :current="stageIndex + 1"
      :total="totalStages"
      :elapsed-seconds="elapsedSeconds"
    />
    <SessionControls
      :can-back="canBack"
      :can-next="canNext"
      :is-last="isLast"
      :primary-label="primaryLabel"
      :loading="loading"
      @back="$emit('back')"
      @next="$emit('next')"
      @continue="$emit('continue')"
      @finish="$emit('finish')"
    />
  </footer>
</template>

<script setup>
import StageProgress from './StageProgress.vue'
import SessionControls from './SessionControls.vue'

defineProps({
  stageIndex: { type: Number, default: 0 },
  totalStages: { type: Number, default: 1 },
  elapsedSeconds: { type: Number, default: 0 },
  canBack: { type: Boolean, default: false },
  canNext: { type: Boolean, default: true },
  isLast: { type: Boolean, default: false },
  primaryLabel: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['back', 'next', 'continue', 'finish'])
</script>

<style scoped>
.session-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 4px 0;
  position: sticky;
  bottom: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    var(--page-bg, #f4f7fb) 28%
  );
  padding-block-start: 20px;
  padding-block-end: 8px;
}
</style>
