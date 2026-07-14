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
    <v-tab value="reading" :to="ROUTES.STUDENT_LANGUAGES_READING">📖 Reading</v-tab>
    <v-tab value="listening" :to="ROUTES.STUDENT_LANGUAGES_LISTENING">🎧 Listen</v-tab>
    <v-tab value="vocabulary" :to="ROUTES.STUDENT_LANGUAGES_VOCABULARY">📚 Vocabulary</v-tab>
    <v-tab value="dictionary" :to="ROUTES.STUDENT_LANGUAGES_DICTIONARY">📖 Dictionary</v-tab>
    <v-tab value="writing" :to="ROUTES.STUDENT_LANGUAGES_WRITING">✍️ Writing</v-tab>
    <v-tab value="speaking" :to="ROUTES.STUDENT_LANGUAGES_SPEAKING">🎤 Speaking</v-tab>
    <v-tab value="curriculum" :to="ROUTES.STUDENT_LANGUAGES_CURRICULUM">🗺️ Curriculum</v-tab>
    <v-tab value="lessons" :to="ROUTES.STUDENT_LANGUAGES_LESSONS">📘 Lessons</v-tab>
    <v-tab value="progress" :to="ROUTES.STUDENT_LANGUAGES_PROGRESS">📊 Progress</v-tab>
    <v-tab value="insights" :to="ROUTES.STUDENT_LANGUAGES_INSIGHTS">🧠 AI Insights</v-tab>
    <v-tab value="history" :to="ROUTES.STUDENT_LANGUAGES_HISTORY">🕓 History</v-tab>
    <v-tab value="exam" :to="ROUTES.STUDENT_LANGUAGES_EXAM">🎓 AI Exam</v-tab>
    <v-tab value="certificates" :to="ROUTES.STUDENT_LANGUAGES_CERTIFICATES">🏅 Certificates</v-tab>
  </v-tabs>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ROUTES } from '../../constants/app.js'
import { useLanguageAccess } from '../../composables/useLanguageAccess.js'

const route = useRoute()
const { access } = useLanguageAccess()

// Per-feature neon accent (R,G,B). Drives the whole Neon Glass theme.
const NEON = {
  hub: '34, 211, 238',
  reading: '34, 211, 238',
  listening: '167, 139, 250',
  vocabulary: '52, 211, 153',
  dictionary: '52, 211, 153',
  writing: '251, 146, 60',
  speaking: '244, 114, 182',
  curriculum: '132, 204, 22',
  lessons: '96, 165, 250',
  progress: '96, 165, 250',
  insights: '124, 108, 240',
  history: '148, 163, 184',
  exam: '250, 204, 21',
  certificates: '250, 204, 21',
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
  if (path.includes('/curriculum')) return 'curriculum'
  if (path.includes('/lessons')) return 'lessons'
  if (path.includes('/insights')) return 'insights'
  if (path.includes('/progress')) return 'progress'
  if (path.includes('/history')) return 'history'
  if (path.includes('/exam')) return 'exam'
  if (path.includes('/certificates')) return 'certificates'
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
onMounted(applyTheme)
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
