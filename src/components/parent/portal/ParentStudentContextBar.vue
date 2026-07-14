<template>
  <v-card v-if="context" class="student-context-bar glass-card pa-4 mb-5" variant="flat">
    <div class="d-flex align-center flex-wrap gap-4">
      <v-avatar size="48" class="eduspark-gradient">
        <span class="text-subtitle-1 font-weight-bold text-white">{{ initials }}</span>
      </v-avatar>
      <div class="flex-grow-1">
        <p class="text-h6 font-weight-bold mb-1">{{ context.name }}</p>
        <div class="d-flex align-center flex-wrap gap-2">
          <v-chip v-if="context.grade_label" size="small" variant="tonal" color="primary">
            {{ context.grade_label }}
          </v-chip>
          <v-chip
            size="small"
            variant="flat"
            :color="statusColor"
            :prepend-icon="statusIcon"
          >
            {{ context.academic_status_label || t('parent.common.emDash') }}
          </v-chip>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  context: { type: Object, default: null },
})

const { t } = useI18n()

const initials = computed(() => {
  const parts = String(props.context?.name || '?').split(' ')
  return parts.slice(0, 2).map((p) => p[0]).join('')
})

const statusColor = computed(() => {
  const s = props.context?.academic_status
  if (s === 'active_now') return 'success'
  if (s === 'active_today') return 'info'
  return 'grey'
})

const statusIcon = computed(() => {
  const s = props.context?.academic_status
  if (s === 'active_now') return 'mdi-circle-medium'
  if (s === 'active_today') return 'mdi-clock-outline'
  return 'mdi-account-off-outline'
})
</script>

<style scoped>
.student-context-bar {
  border-inline-start: 3px solid rgba(124, 108, 240, 0.5);
}
</style>
