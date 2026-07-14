<template>
  <v-chip
    :color="config.color"
    :variant="variant"
    size="small"
    class="status-badge"
    :class="{ 'status-badge--pulse': status === 'processing' }"
  >
    <v-progress-circular
      v-if="status === 'processing'"
      indeterminate
      size="14"
      width="2"
      class="me-1"
    />
    <v-icon v-else-if="config.icon" :icon="config.icon" size="14" class="me-1" />
    {{ config.label }}
  </v-chip>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { LESSON_STATUS } from '../../constants/app.js'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (v) =>
      ['processed', 'processing', 'draft', 'error'].includes(v),
  },
  variant: { type: String, default: 'tonal' },
})

const { t } = useI18n()

const statusMeta = {
  [LESSON_STATUS.PROCESSED]: { labelKey: 'common.lessonStatus.processed', color: 'success', icon: 'mdi-check-circle' },
  [LESSON_STATUS.PROCESSING]: { labelKey: 'common.lessonStatus.processing', color: 'warning', icon: null },
  [LESSON_STATUS.DRAFT]: { labelKey: 'common.lessonStatus.draft', color: 'grey', icon: 'mdi-pencil' },
  [LESSON_STATUS.ERROR]: { labelKey: 'common.lessonStatus.error', color: 'error', icon: 'mdi-alert-circle' },
}

const config = computed(() => {
  const meta = statusMeta[props.status] ?? statusMeta[LESSON_STATUS.DRAFT]
  return { ...meta, label: t(meta.labelKey) }
})
</script>

<style scoped>
.status-badge--pulse {
  animation: badge-glow 2s ease-in-out infinite;
}

@keyframes badge-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.3); }
  50% { box-shadow: 0 0 12px 2px rgba(251, 191, 36, 0.25); }
}
</style>
