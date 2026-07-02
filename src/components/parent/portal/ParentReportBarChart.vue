<template>
  <div class="bar-chart d-flex align-end justify-space-between gap-1">
    <div
      v-for="point in points"
      :key="point.date || point.label"
      class="bar-col text-center flex-grow-1"
    >
      <div class="bar-track">
        <div
          class="bar-fill"
          :class="{ 'bar-fill--zero': !point.value }"
          :style="{ height: heightFor(point.value) }"
        />
      </div>
      <p class="text-caption mb-0 mt-1 text-truncate">{{ point.label }}</p>
      <p class="text-caption text-medium-emphasis mb-0">{{ formatValue(point.value) }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { barHeight, maxTrendValue } from '../../../composables/useParentHistoricalReports.js'

const props = defineProps({
  points: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
})

const { t } = useI18n()

const maxVal = computed(() => maxTrendValue(props.points))

function heightFor(value) {
  return barHeight(value, maxVal.value)
}

function formatValue(v) {
  if (props.unit === '%') return `${v}%`
  if (props.unit === 'min') return t('parent.common.minutesShortWithValue', { n: v })
  return v
}
</script>

<style scoped>
.bar-chart {
  min-height: 140px;
  padding-top: 8px;
}
.bar-col {
  min-width: 0;
  max-width: 72px;
}
.bar-track {
  height: 100px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.bar-fill {
  width: 70%;
  max-width: 36px;
  border-radius: 6px 6px 2px 2px;
  background: linear-gradient(180deg, rgba(var(--v-theme-primary), 0.9), rgba(var(--v-theme-secondary), 0.7));
  transition: height 0.3s ease;
}
.bar-fill--zero {
  background: rgba(255, 255, 255, 0.08);
}
</style>
