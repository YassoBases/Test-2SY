<template>
  <div class="consistency-bars">
    <p class="text-caption font-weight-bold text-medium-emphasis mb-3">{{ t('student.attendance.recentWeeksCommitment') }}</p>
    <div class="d-flex align-end gap-3 bars-row">
      <div
        v-for="bar in bars"
        :key="bar.week_label"
        class="bar-col flex-grow-1 text-center"
      >
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{ height: `${Math.max(8, bar.consistency)}%` }"
          />
        </div>
        <p class="text-caption font-weight-bold mt-2 mb-0">{{ bar.consistency }}%</p>
        <p class="text-caption text-medium-emphasis mb-0">{{ bar.week_label }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  bars: { type: Array, default: () => [] },
})

const { t } = useI18n()
</script>

<style scoped>
.bar-track {
  height: 72px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, var(--em-cyan, #22d3ee), rgba(124, 108, 240, 0.6));
  border-radius: 6px 6px 0 0;
  transition: height 0.4s ease;
}
</style>
