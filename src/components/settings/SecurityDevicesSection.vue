<template>
  <v-card class="glass-card pa-4 pa-md-6" variant="flat">
    <div class="d-flex flex-column flex-sm-row align-sm-center justify-space-between gap-3 mb-4">
      <div>
        <h3 class="text-h6 font-weight-bold d-flex align-center gap-2 mb-1">
          <v-icon color="primary">mdi-shield-lock-outline</v-icon>
          {{ t('settings.devices.title') }}
        </h3>
        <p class="text-body-2 text-medium-emphasis mb-0">
          {{ t('settings.devices.subtitle') }}
        </p>
      </div>
      <v-btn
        variant="tonal"
        color="primary"
        size="small"
        prepend-icon="mdi-refresh"
        :loading="loading"
        @click="loadSessions"
      >
        {{ t('common.refresh') }}
      </v-btn>
    </div>

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-4 rounded-lg"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>

    <div v-if="loading && !sessions.length" class="py-8 text-center">
      <v-progress-circular indeterminate color="primary" />
      <p class="text-body-2 text-medium-emphasis mt-3 mb-0">{{ t('settings.devices.loadingDevices') }}</p>
    </div>

    <v-alert
      v-else-if="!loading && !sessions.length"
      type="info"
      variant="tonal"
      class="rounded-lg"
    >
      {{ t('settings.devices.noSessions') }}
    </v-alert>

    <div v-else class="session-list d-flex flex-column gap-3">
      <v-card
        v-for="item in sessions"
        :key="item.id"
        class="session-card pa-4"
        :class="{ 'session-card--current': item.isCurrent }"
        variant="flat"
      >
        <div class="d-flex flex-column flex-sm-row gap-3">
          <div class="d-flex gap-3 flex-grow-1 min-width-0">
            <v-avatar
              :color="item.isCurrent ? 'primary' : undefined"
              :variant="item.isCurrent ? 'flat' : 'tonal'"
              size="48"
              class="flex-shrink-0"
            >
              <v-icon :color="item.isCurrent ? 'white' : 'primary'">
                {{ deviceTypeIcon(item.deviceType) }}
              </v-icon>
            </v-avatar>

            <div class="min-width-0 flex-grow-1">
              <div class="d-flex flex-wrap align-center gap-2 mb-1">
                <span class="text-subtitle-1 font-weight-bold text-truncate">
                  {{ deviceTitle(item) }}
                </span>
                <v-chip
                  v-if="item.isCurrent"
                  color="success"
                  size="x-small"
                  variant="flat"
                  label
                >
                  {{ t('settings.devices.thisDevice') }}
                </v-chip>
              </div>

              <div class="text-body-2 text-medium-emphasis mb-1">
                <v-icon size="14" class="me-1">mdi-web</v-icon>
                {{ browserLabel(item) }}
              </div>

              <div
                v-if="item.userAgent"
                class="text-caption text-medium-emphasis session-ua mb-2"
                :title="item.userAgent"
              >
                {{ formatUserAgentDetail(item.userAgent) }}
              </div>

              <div class="session-meta d-flex flex-wrap gap-x-4 gap-y-1 text-caption text-medium-emphasis">
                <span>
                  <v-icon size="14" class="me-1">mdi-ip-network</v-icon>
                  {{ item.ipAddress || '—' }}
                </span>
                <span>
                  <v-icon size="14" class="me-1">mdi-clock-outline</v-icon>
                  {{ t('settings.devices.lastActive', { time: formatLastSeen(item.lastSeenAt) }) }}
                </span>
              </div>
            </div>
          </div>

          <div class="d-flex flex-column flex-sm-row align-stretch align-sm-center gap-2 flex-shrink-0">
            <v-btn
              v-if="item.isCurrent"
              variant="outlined"
              color="error"
              size="small"
              block
              class="flex-sm-grow-0"
              :loading="actionId === 'current'"
              prepend-icon="mdi-logout"
              @click="confirmLogoutCurrent"
            >
              {{ t('settings.devices.signOut') }}
            </v-btn>
            <v-btn
              v-else
              variant="tonal"
              color="error"
              size="small"
              block
              class="flex-sm-grow-0"
              :loading="actionId === item.id"
              prepend-icon="mdi-cellphone-link-off"
              @click="confirmRevoke(item)"
            >
              {{ t('settings.devices.endSession') }}
            </v-btn>
          </div>
        </div>
      </v-card>
    </div>

    <v-divider class="my-5" />

    <div class="d-flex flex-column flex-sm-row gap-3">
      <v-btn
        variant="outlined"
        color="error"
        prepend-icon="mdi-logout"
        :loading="actionId === 'current'"
        block
        class="flex-sm-grow-1"
        @click="confirmLogoutCurrent"
      >
        {{ t('settings.devices.signOutThisDevice') }}
      </v-btn>
      <v-btn
        variant="flat"
        color="error"
        prepend-icon="mdi-shield-off-outline"
        :loading="revokingAll"
        block
        class="flex-sm-grow-1"
        @click="confirmRevokeAll"
      >
        {{ t('settings.devices.signOutAllBtn') }}
      </v-btn>
    </div>

    <v-dialog v-model="confirmOpen" max-width="420">
      <v-card class="glass-card pa-5">
        <v-card-title class="text-h6 font-weight-bold pa-0 mb-2">
          {{ confirmTitle }}
        </v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis pa-0 mb-4">
          {{ confirmMessage }}
        </v-card-text>
        <v-card-actions class="pa-0 gap-2 flex-column flex-sm-row">
          <v-btn variant="text" block class="flex-sm-grow-1" @click="confirmOpen = false">
            {{ t('common.cancel') }}
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            block
            class="flex-sm-grow-1"
            :loading="confirmLoading"
            @click="runConfirm"
          >
            {{ t('common.confirm') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthSessions } from '../../composables/useAuthSessions.js'
import {
  browserLabel,
  deviceTypeIcon,
  deviceTypeLabel,
  formatLastSeen,
  formatUserAgentDetail,
} from '../../utils/sessionDisplay.js'

const {
  sessions,
  loading,
  actionId,
  revokingAll,
  error,
  loadSessions,
  logoutCurrentDevice,
  revokeSession,
  revokeAllDevices,
} = useAuthSessions()

const { t } = useI18n()

const confirmOpen = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmLoading = ref(false)
let confirmAction = null

onMounted(() => {
  loadSessions()
})

function deviceTitle(item) {
  const name = item.deviceName || deviceTypeLabel(item.deviceType)
  const type = deviceTypeLabel(item.deviceType)
  if (name && name !== type) return `${name} (${type})`
  return name || type
}

function openConfirm({ title, message, action }) {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmAction = action
  confirmOpen.value = true
}

function confirmLogoutCurrent() {
  openConfirm({
    title: t('settings.devices.signOutThisDevice'),
    message: t('settings.devices.signOutThisDeviceMsg'),
    action: logoutCurrentDevice,
  })
}

function confirmRevoke(item) {
  if (item.isCurrent) {
    confirmLogoutCurrent()
    return
  }
  openConfirm({
    title: t('settings.devices.signOutDevice'),
    message: t('settings.devices.signOutDeviceMsg', { device: deviceTitle(item) }),
    action: () => revokeSession(item.id),
  })
}

function confirmRevokeAll() {
  openConfirm({
    title: t('settings.devices.signOutAll'),
    message: t('settings.devices.signOutAllMsg'),
    action: revokeAllDevices,
  })
}

async function runConfirm() {
  if (!confirmAction) return
  confirmLoading.value = true
  try {
    await confirmAction()
    confirmOpen.value = false
  } finally {
    confirmLoading.value = false
  }
}
</script>

<style scoped>
.session-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.5);
}

.session-card--current {
  border-color: rgba(var(--v-theme-primary), 0.35);
  background: rgba(var(--v-theme-primary), 0.06);
}

.session-ua {
  word-break: break-word;
  line-height: 1.4;
}

.min-width-0 {
  min-width: 0;
}
</style>
