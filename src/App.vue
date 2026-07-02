<template>
  <v-app class="eduspark-app">
    <div class="app-ambient" :class="`app-ambient--${mode}`" aria-hidden="true">
      <div class="app-ambient__orb app-ambient__orb--1" />
      <div class="app-ambient__orb app-ambient__orb--2" />
      <div class="app-ambient__orb app-ambient__orb--3" />
    </div>
    <div class="page-content">
      <router-view />
    </div>
    <AppToast />
  </v-app>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheme } from 'vuetify'
import AppToast from './components/common/AppToast.vue'
import { bindVuetifyTheme, useThemeMode } from './composables/useThemeMode.js'
import { useAppLocale } from './composables/useAppLocale.js'

const { mode } = useThemeMode()
const theme = useTheme()
const { t, locale } = useI18n()
useAppLocale()

function syncDocumentTitle() {
  document.title = t('common.appTitle')
}

onMounted(() => {
  bindVuetifyTheme(theme)
  syncDocumentTitle()
})

watch(locale, syncDocumentTitle)
</script>

<style scoped>
.eduspark-app {
  min-height: 100vh;
}
</style>
