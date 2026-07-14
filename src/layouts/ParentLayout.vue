<template>
  <v-layout class="parent-layout">
    <ParentSidebar v-model:drawer="drawer" />

    <v-main class="parent-main">
      <AppHeader
        :title="pageTitle"
        role="parent"
        @toggle-drawer="drawer = !drawer"
      />
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
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import ParentSidebar from '../components/layout/ParentSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'
import { provideParentShell } from '../composables/useParentShell.js'
import { resolveRouteTitle } from '../utils/routeTitle.js'

const { t } = useI18n()
const drawer = ref(true)
const route = useRoute()
const pageTitle = computed(() => {
  const resolved = resolveRouteTitle(route, t)
  if (resolved) return resolved
  return t('dashboard.parent.defaultPageTitle')
})

const shell = provideParentShell()
onMounted(() => shell.init())
</script>

<style scoped>
.parent-layout {
  min-height: 100vh;
}

.parent-main {
  background: transparent;
}
</style>
