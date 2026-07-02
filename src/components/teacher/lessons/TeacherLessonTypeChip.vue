<template>
  <span class="lesson-type-chip">
    <v-icon :icon="meta.icon" size="14" class="lesson-type-chip__icon" />
    {{ meta.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  contentType: { type: String, default: '' },
  label: { type: String, default: '' },
})

const TYPE_META = {
  video: { key: 'teacher.labels.video', icon: 'mdi-play-circle-outline' },
  pdf: { key: 'teacher.labels.pdf', icon: 'mdi-file-pdf-box' },
  homework: { key: 'teacher.labels.homework', icon: 'mdi-clipboard-text-outline' },
  ai: { key: 'teacher.labels.ai', icon: 'mdi-brain' },
  composite: { key: 'teacher.labels.composite', icon: 'mdi-layers-outline' },
  audio: { key: 'teacher.labels.audio', icon: 'mdi-headphones' },
}

const meta = computed(() => {
  const key = String(props.contentType || '').toLowerCase()
  const known = TYPE_META[key]
  if (known) {
    return { label: t(known.key), icon: known.icon }
  }
  return {
    label: props.label || key || t('teacher.labels.lessonDefault'),
    icon: 'mdi-book-open-page-variant-outline',
  }
})
</script>
