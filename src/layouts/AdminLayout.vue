<template>
  <v-layout class="admin-layout">
    <v-main class="admin-main">
      <v-app-bar flat class="app-header glass-header px-2 px-md-4">
        <v-btn icon variant="text" :to="backTo">
          <v-icon>mdi-arrow-right</v-icon>
        </v-btn>
        <v-toolbar-title class="text-h6 font-weight-bold">
          {{ pageTitle }}
        </v-toolbar-title>
        <v-spacer />
        <LanguageSwitcher />
        <v-btn variant="text" prepend-icon="mdi-logout" @click="logout">
          {{ t('common.admin.logoutShort') }}
        </v-btn>
      </v-app-bar>
      <v-container fluid class="page-container pa-4 pa-md-6">
        <router-view v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import LanguageSwitcher from '../components/common/LanguageSwitcher.vue'
import { useAuth } from '../composables/useAuth.js'
import { resolvePostAuthRoute } from '../utils/studentFlow.js'
import { getSession } from '../utils/session.js'
import { resolveRouteTitle } from '../utils/routeTitle.js'

const { t } = useI18n()
const route = useRoute()
const { logout } = useAuth()

const pageTitle = computed(() => {
  const resolved = resolveRouteTitle(route, t)
  return resolved || t('common.admin.defaultTitle')
})

const backTo = computed(() => {
  const session = getSession()
  return resolvePostAuthRoute(session) || '/'
})
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}
</style>
