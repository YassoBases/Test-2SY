<template>
  <GrammarShell>
    <template v-if="loading && !levels.length">
      <v-skeleton-loader type="article" />
    </template>
    <GrammarReviewPanel
      v-else
      :completed-by-level="completedByLevel"
      @select-stage="onSelectStage"
    />

    <template #sidebar>
      <GrammarEngineSidebar
        :current-name="currentStage?.display_name || ''"
        :cefr="progress?.cefr_label || currentStage?.cefr || ''"
        :confidence="averageConfidence"
        :mastery="currentStage?.overall_mastery || 0"
        :next-name="nextStage?.display_name || ''"
        :minutes="estimatedMinutes"
        :recommendation="recommendation"
      />
    </template>
  </GrammarShell>
</template>

<script setup>
import { onMounted } from 'vue'
import { useGrammarEngineHome } from '../../../composables/useGrammarEngineHome.js'
import GrammarShell from '../../../components/grammar-v2/GrammarShell.vue'
import GrammarReviewPanel from '../../../components/grammar-v2/GrammarReviewPanel.vue'
import GrammarEngineSidebar from '../../../components/grammar-v2/GrammarEngineSidebar.vue'

const {
  loading,
  levels,
  progress,
  currentStage,
  nextStage,
  completedByLevel,
  averageConfidence,
  estimatedMinutes,
  recommendation,
  canOpenStage,
  loadHome,
  openStage,
} = useGrammarEngineHome()

function onSelectStage(stage) {
  if (!canOpenStage(stage) || stage.status !== 'completed') return
  openStage(stage)
}

onMounted(() => loadHome())
</script>
