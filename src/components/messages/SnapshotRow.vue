<template>
  <div class="snapshot-row mb-2">
    <div class="d-flex align-center gap-2 mb-1">
      <v-icon size="16" color="primary">{{ icon }}</v-icon>
      <span class="text-caption font-weight-bold">{{ label }}</span>
    </div>
    <div class="text-body-2">{{ item.title }}</div>
    <div v-if="item.subtitle" class="text-caption text-medium-emphasis text-truncate">{{ item.subtitle }}</div>
    <div v-if="item.occurred_at" class="text-caption text-medium-emphasis mt-1">{{ formatDate(item.occurred_at) }}</div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  icon: { type: String, default: 'mdi-information' },
  label: { type: String, required: true },
  item: { type: Object, required: true },
})

const { locale } = useI18n()

function formatDate(iso) {
  if (!iso) return ''
  try {
    const dateLocale = locale.value === 'ar' ? 'ar-SY' : 'en-US'
    return new Intl.DateTimeFormat(dateLocale, { dateStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>

<style scoped>
.snapshot-row {
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(15, 20, 35, 0.4);
}
</style>
