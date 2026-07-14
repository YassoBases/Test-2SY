<template>
  <span class="lesson-status-badge" :class="`lesson-status-badge--${meta.tone}`">
    <span class="lesson-status-badge__dot" aria-hidden="true" />
    {{ meta.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  status: { type: String, default: '' },
})

const STATUS_KEYS = {
  processed: 'teacher.status.ready',
  draft: 'teacher.status.draft',
  processing: 'teacher.status.processing',
  error: 'teacher.labels.statusError',
}

const TONES = {
  processed: 'ready',
  draft: 'draft',
  processing: 'processing',
  error: 'error',
}

const meta = computed(() => {
  const status = props.status
  const key = STATUS_KEYS[status]
  return {
    label: key ? t(key) : (status || '—'),
    tone: TONES[status] || 'draft',
  }
})
</script>
