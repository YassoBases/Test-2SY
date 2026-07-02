<template>
  <v-card class="glass-card pa-5 pa-md-6" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
      <v-icon color="secondary">mdi-history</v-icon>
      {{ t('common.recentActivity.title') }}
    </h3>
    <p v-if="!items.length" class="text-body-2 text-medium-emphasis text-center py-6 mb-0">
      {{ t('common.recentActivity.empty') }}
    </p>
    <v-timeline v-else side="end" density="compact" truncate-line="both" class="activity-timeline">
      <v-timeline-item
        v-for="(item, idx) in items"
        :key="item.id || idx"
        :dot-color="item.color || 'secondary'"
        size="small"
      >
        <div class="d-flex align-start gap-2">
          <v-icon v-if="item.icon" :icon="item.icon" :color="item.color" size="18" class="mt-1" />
          <div>
            <div class="text-body-2 font-weight-medium">{{ item.title }}</div>
            <div v-if="item.time" class="text-caption text-medium-emphasis">{{ item.time }}</div>
          </div>
        </div>
      </v-timeline-item>
    </v-timeline>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
defineProps({
  items: { type: Array, required: true },
})
</script>

<style scoped>
.activity-timeline :deep(.v-timeline-divider__dot) {
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.25);
}
</style>
