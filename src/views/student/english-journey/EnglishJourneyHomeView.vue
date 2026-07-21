<template>
  <JourneyShell class="english-journey-home">
    <template v-if="loading && !journey">
      <v-skeleton-loader type="article, article, article" class="mb-4" />
    </template>

    <template v-else-if="errorMessage === 'load' && !journey">
      <JourneyEmptyState
        icon="mdi-alert-circle-outline"
        :title="t('student.englishJourney.errors.load')"
        :action-label="t('student.englishJourney.session.backHome')"
        @action="loadJourney()"
      />
    </template>

    <template v-else>
      <v-alert
        v-if="!teacherEnabled"
        type="info"
        variant="tonal"
        class="mb-4 rounded-lg"
      >
        {{ t('student.englishJourney.empty.teacherOff') }}
      </v-alert>

      <JourneyEmptyState
        v-if="!levels.length"
        icon="mdi-robot-outline"
        :title="t('student.englishJourney.empty.disabledTitle')"
        :description="t('student.englishJourney.empty.disabledBody')"
      />

      <!-- Journey-first layout: AI Teacher Hero → Progress → Timeline/Stages → Session Entry -->
      <template v-else>
        <JourneyHero
          :name="studentName"
          :current-label="currentStage?.display_name || ''"
          :goal="todayGoal"
          :cefr="progress?.cefr_label || currentStage?.cefr || ''"
          :streak="streakDays"
          :minutes="sessionMinutes"
          :loading="starting"
          :disabled="!teacherEnabled || !currentGrammarId"
          @start="startTodaysSession()"
        />

        <JourneyProgressBar v-if="progress" :progress="progress" class="mb-6" />

        <LevelTimeline :levels="levels" @select-stage="onSelectStage" />

        <SessionEntryCard
          :title="sessionEntryTitle"
          :subtitle="currentStage?.display_name || ''"
          :mission="teacherSession?.mission || null"
          :sections="teacherSession?.sections || []"
          :minutes="sessionMinutes"
          :loading="starting"
          :disabled="!teacherEnabled || !currentGrammarId"
          :stage-to="currentStageRoute"
          @start="startTodaysSession()"
        />
      </template>
    </template>

    <template #sidebar>
      <AiTeacherSidebar
        :mission="teacherSession?.mission || null"
        :energy="teacherSession?.energy || null"
        :confidence="averageConfidence"
        :next-milestone="nextStage?.display_name || currentStage?.display_name || ''"
      />
    </template>
  </JourneyShell>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEnglishJourney } from '../../../composables/useEnglishJourney.js'
import { ROUTES } from '../../../constants/app.js'
import JourneyShell from '../../../components/english-journey/JourneyShell.vue'
import JourneyHero from '../../../components/english-journey/JourneyHero.vue'
import JourneyProgressBar from '../../../components/english-journey/JourneyProgressBar.vue'
import LevelTimeline from '../../../components/english-journey/LevelTimeline.vue'
import SessionEntryCard from '../../../components/english-journey/SessionEntryCard.vue'
import AiTeacherSidebar from '../../../components/english-journey/AiTeacherSidebar.vue'
import JourneyEmptyState from '../../../components/english-journey/JourneyEmptyState.vue'

const { t } = useI18n()
const {
  journey,
  loading,
  starting,
  errorMessage,
  studentName,
  progress,
  levels,
  currentGrammarId,
  currentStage,
  nextStage,
  streakDays,
  averageConfidence,
  sessionMinutes,
  todayGoal,
  teacherEnabled,
  teacherSession,
  loadJourney,
  startTodaysSession,
  openStage,
  canOpenStage,
  hydrateSession,
} = useEnglishJourney()

const sessionEntryTitle = computed(() =>
  t('student.englishJourney.sessionEntry.titleWithStage', {
    stage: currentStage.value?.display_name || t('student.englishJourney.hero.currentStage'),
  }),
)

const currentStageRoute = computed(() =>
  currentGrammarId.value ? ROUTES.STUDENT_ENGLISH_JOURNEY_STAGE(currentGrammarId.value) : '',
)

function onSelectStage(stage) {
  if (!canOpenStage(stage)) return
  openStage(stage.grammar_id)
}

onMounted(() => {
  hydrateSession()
  loadJourney()
})
</script>

<style scoped>
.english-journey-home :deep(.journey-shell__main) {
  min-width: 0;
}
</style>
