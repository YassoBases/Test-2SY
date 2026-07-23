<template>
  <GrammarShell>
    <template v-if="statusLoading || (loading && !levels.length)">
      <v-skeleton-loader type="article, article, article" />
    </template>

    <v-alert
      v-else-if="isReady && !isEnabled"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
    >
      {{ t('student.grammarV2.empty.disabled') }}
    </v-alert>

    <AppEmptyState
      v-else-if="errorMessage === 'load' && !levels.length"
      icon="mdi-alert-circle-outline"
      :title="t('student.grammarV2.errors.load')"
      :action-label="t('student.grammarV2.review.backHome')"
      @action="loadHome()"
    />

    <AppEmptyState
      v-else-if="!levels.length"
      icon="mdi-book-outline"
      :title="t('student.grammarV2.empty.noRoadmap')"
      :description="t('student.grammarV2.empty.noRoadmapHint')"
    />

    <template v-else>
      <v-alert
        v-if="actionError"
        type="error"
        variant="tonal"
        class="mb-4 rounded-lg"
        closable
        @click:close="clearActionError"
      >
        {{ actionError }}
      </v-alert>

      <GrammarHeroV2
        :current-name="currentStage?.display_name || ''"
        :cefr="progress?.cefr_label || currentStage?.cefr || anchorCefr || ''"
        :stage-index="progress?.stage_index || 0"
        :stage-total="progress?.stage_total_in_level || 0"
        :completed="progress?.overall_completed || 0"
        :total="progress?.overall_total || stageCount"
        :percent="overallPercent"
        :minutes="estimatedMinutes"
        :loading="starting"
        :can-start="canStartLessonFor(currentStage)"
        @start="onStartLesson"
      />

      <GrammarProgressPanel
        :completed="progress?.overall_completed || 0"
        :total="progress?.overall_total || stageCount"
        :cefr="progress?.cefr_label || currentStage?.cefr || anchorCefr || ''"
        :stage-index="progress?.stage_index || 0"
        :stage-total="progress?.stage_total_in_level || 0"
        :remaining="remainingTopics"
        :percent="overallPercent"
      />

      <GrammarCefrRoadmap
        :levels="levels"
        :anchor-cefr="anchorCefr"
        :can-open-stage="canOpenStage"
        @select-stage="onSelectStage"
      />
    </template>

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
import { useI18n } from 'vue-i18n'
import { useGrammarEngineHome } from '../../../composables/useGrammarEngineHome.js'
import GrammarShell from '../../../components/grammar-v2/GrammarShell.vue'
import GrammarHeroV2 from '../../../components/grammar-v2/GrammarHeroV2.vue'
import GrammarProgressPanel from '../../../components/grammar-v2/GrammarProgressPanel.vue'
import GrammarCefrRoadmap from '../../../components/grammar-v2/GrammarCefrRoadmap.vue'
import GrammarEngineSidebar from '../../../components/grammar-v2/GrammarEngineSidebar.vue'
import AppEmptyState from '../../../components/ui/AppEmptyState.vue'

const { t } = useI18n()
const {
  loading,
  starting,
  errorMessage,
  actionError,
  isEnabled,
  isReady,
  statusLoading,
  levels,
  progress,
  anchorCefr,
  currentStage,
  nextStage,
  stageCount,
  remainingTopics,
  overallPercent,
  estimatedMinutes,
  averageConfidence,
  recommendation,
  canStartLessonFor,
  canOpenStage,
  loadHome,
  startCurrentLesson,
  openStage,
} = useGrammarEngineHome()

function onSelectStage(stage) {
  if (!canOpenStage(stage)) return
  openStage(stage)
}

async function onStartLesson() {
  await startCurrentLesson({ navigate: true })
}

function clearActionError() {
  actionError.value = ''
}

onMounted(() => {
  loadHome()
})
</script>
