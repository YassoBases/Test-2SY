<template>
  <header class="onboarding-account-header">
    <div class="onboarding-account-header__actions">
      <v-btn
        variant="text"
        size="small"
        class="logout-btn d-none d-sm-inline-flex"
        prepend-icon="mdi-logout"
        :loading="loggingOut"
        @click="onLogout"
      >
        {{ t('common.logout') }}
      </v-btn>

      <v-menu location="bottom end" offset="6">
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            variant="tonal"
            size="small"
            rounded="lg"
            class="account-btn"
            color="primary"
          >
            <v-icon start size="18">mdi-account-circle-outline</v-icon>
            <span class="account-btn__name">{{ displayName }}</span>
            <v-icon end size="16">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list density="compact" class="account-menu" rounded="lg" min-width="220">
          <v-list-item :title="displayName" :subtitle="email" class="account-menu__identity" />
          <v-divider class="my-1" />
          <v-list-item
            prepend-icon="mdi-logout"
            :title="t('common.logout')"
            :disabled="loggingOut"
            @click="onLogout"
          />
        </v-list>
      </v-menu>

      <v-btn
        icon
        variant="text"
        size="small"
        class="logout-btn-icon d-sm-none"
        :aria-label="t('common.logout')"
        :loading="loggingOut"
        @click="onLogout"
      >
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth.js'
import { getSession } from '../../utils/session.js'

const { t } = useI18n()
const { logout } = useAuth()
const loggingOut = ref(false)

const session = computed(() => getSession())
const displayName = computed(
  () => session.value?.name?.trim() || t('auth.onboarding.accountHeader.studentFallback'),
)
const email = computed(() => session.value?.email || '')

async function onLogout() {
  if (loggingOut.value) return
  loggingOut.value = true
  try {
    await logout()
  } finally {
    loggingOut.value = false
  }
}
</script>

<style scoped>
.onboarding-account-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 1rem;
  min-height: 40px;
}

.onboarding-account-header__actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.account-btn {
  max-width: min(58vw, 240px);
  text-transform: none;
  letter-spacing: 0;
}

.account-btn__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  font-size: 0.8rem;
}

.logout-btn {
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.8rem;
  opacity: 0.9;
}

.account-menu__identity :deep(.v-list-item-title) {
  font-weight: 700;
  font-size: 0.875rem;
}

.account-menu__identity :deep(.v-list-item-subtitle) {
  font-size: 0.75rem;
  opacity: 0.75;
}
</style>
