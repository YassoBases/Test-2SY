<template>
  <v-tabs
    v-if="showTabs"
    :model-value="activeTab"
    color="secondary"
    show-tabs
    class="language-module-tabs mb-4"
    @update:model-value="onTab"
  >
    <v-tab value="hub" :to="ROUTES.STUDENT_LANGUAGES">Home</v-tab>
    <v-tab value="reading" :to="ROUTES.STUDENT_LANGUAGES_READING">Reading</v-tab>
    <v-tab value="listening" :to="ROUTES.STUDENT_LANGUAGES_LISTENING">Listen</v-tab>
    <v-tab value="writing" :to="ROUTES.STUDENT_LANGUAGES_WRITING">Writing</v-tab>
    <v-tab value="speaking" :to="ROUTES.STUDENT_LANGUAGES_SPEAKING">Speaking</v-tab>
    <v-tab value="vocabulary" :to="ROUTES.STUDENT_LANGUAGES_VOCABULARY">Vocabulary</v-tab>
    <v-tab value="journey" :to="ROUTES.STUDENT_ENGLISH_JOURNEY">Journey</v-tab>
    <v-tab v-if="grammarEnabled" value="grammar" :to="ROUTES.STUDENT_GRAMMAR">Grammar</v-tab>
  </v-tabs>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ROUTES } from '../../constants/app.js'
import { useLanguageAccess } from '../../composables/useLanguageAccess.js'
import { useGrammarModule } from '../../composables/useGrammarModule.js'

const route = useRoute()
const { access } = useLanguageAccess()
const { isEnabled: grammarEnabled, refresh: refreshGrammar } = useGrammarModule()

// Per-feature neon accent (R,G,B). Drives the whole Neon Glass theme.
const NEON = {
  hub: '34, 211, 238',
  reading: '96, 165, 250',
  listening: '167, 139, 250',
  writing: '251, 146, 60',
  speaking: '244, 114, 182',
  vocabulary: '52, 211, 153',
  journey: '99, 102, 241',
  grammar: '45, 212, 191',
}

const showTabs = computed(
  () => access.value?.subscribed && access.value?.placement_completed && route.meta.languageModule,
)

const activeTab = computed(() => {
  const path = route.path
  if (path.includes('/reading')) return 'reading'
  if (path.includes('/listening')) return 'listening'
  if (path.includes('/vocabulary')) return 'vocabulary'
  if (path.includes('/writing')) return 'writing'
  if (path.includes('/speaking')) return 'speaking'
  if (path.includes('/english-journey')) return 'journey'
  if (path.includes('/grammar')) return 'grammar'
  return 'hub'
})

function onTab() {
  /* navigation via :to on v-tab */
}

// Apply the Neon Glass theme to the whole language module + set the current feature's accent.
function applyTheme() {
  document.body.classList.add('lang-neon')
  document.body.style.setProperty('--neon', NEON[activeTab.value] || NEON.hub)
}
onMounted(() => {
  refreshGrammar()
  applyTheme()
})
watch(activeTab, applyTheme)
onUnmounted(() => {
  document.body.classList.remove('lang-neon')
  document.body.style.removeProperty('--neon')
})
</script>

<style scoped>
.language-module-tabs :deep(.v-tab) {
  text-transform: none;
  letter-spacing: 0;
}
</style>
