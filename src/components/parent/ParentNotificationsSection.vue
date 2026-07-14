<template>
  <div>
    <ParentNotificationSettingsPanel
      :settings="settings"
      :loading="settingsLoading"
      :saving="savingSettings"
      :error="settingsError"
      @save="$emit('save-settings', $event)"
    />

    <v-card class="glass-card pa-5 mb-6" variant="flat">
      <div class="d-flex align-center gap-2 mb-4 flex-wrap">
        <v-icon color="error">mdi-bell-alert-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.notifications.log.title') }}</h3>
        <v-chip v-if="unreadCount" size="x-small" color="error" variant="flat" class="ms-1">
          {{ t('parent.notifications.log.unread', { n: unreadCount }) }}
        </v-chip>
      </div>

      <v-skeleton-loader v-if="loading" type="list-item@6" />

      <v-alert v-else-if="loadError" type="error" variant="tonal" class="rounded-lg">
        {{ loadError }}
      </v-alert>

      <v-alert v-else-if="!items.length" type="info" variant="tonal" class="rounded-lg">
        {{ t('parent.notifications.log.empty') }}
      </v-alert>

      <v-table v-else density="comfortable" class="notification-table bg-transparent">
        <thead>
          <tr>
            <th>{{ t('parent.notifications.log.type') }}</th>
            <th>{{ t('parent.notifications.log.details') }}</th>
            <th>{{ t('parent.notifications.log.time') }}</th>
            <th>{{ t('parent.notifications.log.status') }}</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            :class="{ 'notification-row--unread': !item.is_read }"
          >
            <td>
              <div class="d-flex align-center gap-2">
                <v-avatar :color="meta(item).color" size="32" variant="tonal">
                  <v-icon size="16">{{ meta(item).icon }}</v-icon>
                </v-avatar>
                <span class="text-body-2">{{ item.category_label || meta(item).label }}</span>
              </div>
            </td>
            <td class="text-body-2 notification-body">{{ item.title }}</td>
            <td class="text-caption text-medium-emphasis">{{ formatNotificationTime(item.created_at) }}</td>
            <td>
              <v-chip
                size="x-small"
                :color="item.is_read ? 'grey' : 'primary'"
                variant="tonal"
              >
                {{ item.is_read ? t('parent.notifications.log.read') : t('parent.notifications.log.new') }}
              </v-chip>
            </td>
            <td class="text-end">
              <v-btn
                v-if="!item.is_read"
                size="x-small"
                variant="text"
                @click="$emit('mark-read', item.id)"
              >
                {{ t('parent.notifications.log.markRead') }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentNotificationSettingsPanel from './portal/ParentNotificationSettingsPanel.vue'
import {
  NOTIFICATION_CATEGORY_META,
  formatNotificationTime,
} from '../../composables/useParentNotifications.js'

defineProps({
  items: { type: Array, default: () => [] },
  unreadCount: { type: Number, default: 0 },
  settings: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  settingsLoading: { type: Boolean, default: false },
  savingSettings: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
  settingsError: { type: String, default: '' },
})

defineEmits(['mark-read', 'save-settings'])

const { t } = useI18n()

function meta(item) {
  const base = NOTIFICATION_CATEGORY_META[item.category] || NOTIFICATION_CATEGORY_META.general
  const key = `parent.notifications.categories.${item.category}`
  const translated = t(key)
  return {
    ...base,
    label: item.category_label || (translated !== key ? translated : base.label),
  }
}
</script>

<style scoped>
.notification-table th {
  font-weight: 600;
  white-space: nowrap;
}
.notification-body {
  white-space: pre-line;
  max-width: 320px;
}
.notification-row--unread {
  background: rgba(var(--v-theme-primary), 0.04);
}
</style>
