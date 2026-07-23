<template>
  <div class="page-container">
    <StageCompletionScreen
      :wrap-up="wrapUp"
      :next-label="nextLabel"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useEnglishJourney } from '../../../composables/useEnglishJourney.js'
import StageCompletionScreen from '../../../components/english-journey/StageCompletionScreen.vue'

const {
  teacherSession,
  nextStage,
  currentStage,
  hydrateSession,
  loadJourney,
} = useEnglishJourney()

const wrapUp = computed(() => teacherSession.value?.wrap_up_preview || null)
const nextLabel = computed(
  () => nextStage.value?.display_name || currentStage.value?.display_name || '',
)

onMounted(async () => {
  hydrateSession()
  await loadJourney({ withAdaptive: false, withTeacherStatus: false })
})
</script>
