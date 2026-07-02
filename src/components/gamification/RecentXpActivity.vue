<template>
  <div v-if="items.length" class="recent-activity">
    <div
      v-for="(item, idx) in items"
      :key="`${item.label}-${idx}`"
      class="recent-activity__row d-flex align-center justify-space-between pa-3 rounded-lg mb-2"
    >
      <div>
        <div class="text-body-2 font-weight-medium">{{ item.label }}</div>
        <div v-if="item.occurred_at" class="text-caption text-medium-emphasis">
          {{ formatDate(item.occurred_at) }}
        </div>
      </div>
      <v-chip
        v-if="item.xp > 0"
        size="small"
        color="success"
        variant="tonal"
      >
        +{{ item.xp }} XP
      </v-chip>
      <v-chip v-else size="small" color="primary" variant="tonal">{{ t('student.achievements.widgets.achievementBadge') }}</v-chip>
    </div>
  </div>
  <p v-else class="text-body-2 text-medium-emphasis mb-0">
    {{ t('student.achievements.widgets.noXpActivity') }}
  </p>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})

const { t, locale } = useI18n()

function formatDate(value) {
  if (!value) return ''
  try {
    const loc = locale.value === 'ar' ? 'ar-SY' : 'en-US'
    return new Date(value).toLocaleString(loc, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}
</script>

<style scoped>
.recent-activity__row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(124, 108, 240, 0.1);
}
</style>
