<template>
  <v-card v-if="alerts.length" class="glass-card pa-4 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-3">
      <v-icon color="warning">mdi-bell-alert-outline</v-icon>
      <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.notifications.overview.title') }}</h3>
      <v-chip v-if="unreadCount" size="x-small" color="error" variant="flat" class="ms-1">
        {{ unreadCount }}
      </v-chip>
      <v-btn
        size="x-small"
        variant="text"
        class="ms-auto"
        :to="viewAllRoute"
      >
        {{ t('parent.notifications.overview.viewAll') }}
      </v-btn>
    </div>
    <v-alert
      v-for="alert in alerts"
      :key="alert.id"
      :type="alert.type === 'error' ? 'error' : alert.type === 'success' ? 'success' : alert.type === 'info' ? 'info' : 'warning'"
      variant="tonal"
      density="compact"
      class="mb-2 rounded-lg"
      :class="{ 'alert-unread': !alert.is_read }"
    >
      <div class="font-weight-medium">{{ alert.title }}</div>
      <div v-if="alert.subtitle" class="text-caption mt-1 opacity-80">{{ alert.subtitle }}</div>
    </v-alert>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

defineProps({
  alerts: { type: Array, default: () => [] },
  unreadCount: { type: Number, default: 0 },
})

const { t } = useI18n()

const viewAllRoute = ROUTES.PARENT_NOTIFICATIONS
</script>

<style scoped>
.alert-unread {
  border-inline-start: 3px solid rgb(var(--v-theme-primary));
}
</style>
