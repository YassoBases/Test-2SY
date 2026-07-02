<template>
  <v-menu v-if="isApiMode()" location="bottom end" :close-on-content-click="false">
    <template #activator="{ props: menuProps }">
      <v-btn icon v-bind="menuProps" class="me-1">
        <v-badge
          v-if="unreadCount > 0"
          :content="unreadCount > 99 ? '99+' : unreadCount"
          color="error"
          overlap
        >
          <v-icon>mdi-bell-outline</v-icon>
        </v-badge>
        <v-icon v-else>mdi-bell-outline</v-icon>
      </v-btn>
    </template>
    <v-card class="glass-card notification-panel" min-width="320" max-width="400">
      <v-card-title class="d-flex align-center justify-space-between py-3">
        <span class="text-subtitle-1 font-weight-bold">{{ t('common.notificationBell.title') }}</span>
        <v-btn
          v-if="unreadCount > 0"
          size="small"
          variant="text"
          @click="markAllRead"
        >
          {{ t('common.notificationBell.markAllRead') }}
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-list v-if="items.length" density="compact" class="py-0">
        <v-list-item
          v-for="n in items"
          :key="n.id"
          :class="{ 'bg-surface-light': !n.is_read }"
          @click="onItemClick(n)"
        >
          <template #prepend>
            <v-icon :color="n.is_read ? 'grey' : 'primary'" size="20">
              {{ iconFor(n.type) }}
            </v-icon>
          </template>
          <v-list-item-title class="text-body-2 font-weight-medium">
            {{ n.title }}
          </v-list-item-title>
          <v-list-item-subtitle class="text-caption">
            {{ n.body }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <div v-else class="notification-panel__empty">
        <div class="notification-panel__empty-icon">
          <v-icon icon="mdi-bell-off-outline" size="28" color="primary" />
        </div>
        <p class="text-body-2 font-weight-medium mb-1">{{ t('common.notificationBell.emptyTitle') }}</p>
        <p class="text-caption text-medium-emphasis mb-0">
          {{ t('common.notificationBell.emptyDescription') }}
        </p>
      </div>
    </v-card>
  </v-menu>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import { useAuth } from '../../composables/useAuth.js'
import { isApiMode } from '../../utils/session.js'

const router = useRouter()
const { t } = useI18n()
const { role } = useAuth()
const { items, unreadCount, markRead, markAllRead } = useNotifications()

function iconFor(type) {
  const map = {
    lesson_published: 'mdi-book-open-page-variant',
    quiz_published: 'mdi-clipboard-check',
    payment_received: 'mdi-cash-check',
    homework_graded: 'mdi-school',
    parent_alert: 'mdi-account-child',
    subscription_expiring: 'mdi-clock-alert',
    internal_message: 'mdi-message-text-outline',
    parent_note: 'mdi-note-text',
    parent_note_reply: 'mdi-reply',
  }
  return map[type] || 'mdi-bell'
}

function messagesPath() {
  const r = role.value
  if (r === 'teacher') return '/teacher/messages'
  if (r === 'parent') return '/parent/messages'
  if (r === 'student') return '/student/messages'
  return null
}

async function onItemClick(n) {
  if (!n.is_read) await markRead(n.id)
  if (n.type === 'internal_message' && n.payload?.thread_id) {
    const base = messagesPath()
    if (base) {
      await router.push({ path: base, query: { thread: n.payload.thread_id } })
    }
  }
}
</script>

<style scoped>
.notification-panel {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
