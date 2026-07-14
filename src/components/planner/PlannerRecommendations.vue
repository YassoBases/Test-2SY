<template>
  <v-card class="glass-card glass-card--solid pa-4" variant="flat">
    <ul v-if="items.length" class="rec-list mb-0">
      <li v-for="(rec, i) in items" :key="i" class="rec-list__item">
        <span class="rec-list__icon">{{ rec.priority_icon || '💡' }}</span>
        <div class="min-w-0">
          <span class="text-body-2">{{ rec.text }}</span>
          <div v-if="rec.priority_label" class="text-caption text-medium-emphasis">
            {{ rec.priority_icon }} {{ rec.priority_label }}
          </div>
        </div>
      </li>
    </ul>
    <p v-else class="text-body-2 text-medium-emphasis mb-0">
      {{ t('common.planner.recommendationsEmpty') }}
    </p>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  items: { type: Array, default: () => [] },
})

const { t } = useI18n()
</script>

<style scoped>
.rec-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.rec-list__item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(124, 108, 240, 0.1);
}

.rec-list__item:last-child {
  border-bottom: none;
}

.rec-list__icon {
  flex-shrink: 0;
  font-size: 1.1rem;
}
</style>
