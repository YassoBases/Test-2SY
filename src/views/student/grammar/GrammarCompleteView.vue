<template>
  <div class="page-container">
    <GrammarCompletionScreen
      :display-name="completionResult?.display_name || ''"
      :mastery="completionResult?.overall_mastery || 0"
      :confidence="completionResult?.confidence || averageConfidence"
      :skills="completionResult?.skills || []"
      :next-name="completionResult?.next_display_name || nextStage?.display_name || ''"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGrammarEngineHome } from '../../../composables/useGrammarEngineHome.js'
import GrammarCompletionScreen from '../../../components/grammar-v2/GrammarCompletionScreen.vue'
import { ROUTES } from '../../../constants/app.js'

const router = useRouter()
const {
  completionResult,
  averageConfidence,
  nextStage,
  hydrateCompletion,
  loadHome,
} = useGrammarEngineHome()

onMounted(async () => {
  hydrateCompletion()
  await loadHome()
  if (!completionResult.value) {
    router.replace(ROUTES.STUDENT_GRAMMAR)
  }
})
</script>
