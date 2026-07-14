<template>
  <div class="speaking-lesson-experience slide-up-enter-active">
    <SpeakingMissionHeader
      :lesson-title="lessonTitle"
      :focus-label="focusLabel"
      :focus-reason="focusReason"
      :plan-summary="planSummary"
      :official-cefr="officialCefr"
      :current-mission="currentMission"
      :next-mission="nextMission"
      :current-task="currentTask"
      :attempt="attempt"
      :objectives="objectives"
      :expected-outcome="expectedOutcome"
    />

    <SpeakingLessonProgress
      :current-mission="currentMission"
      :current-activity-title="currentActivityTitle"
      :activities-total="activitiesTotal"
      :activities-completed="activitiesCompleted"
      :activities-remaining="activitiesRemaining"
    />

    <SpeakingMissionTimeline :learning-path="learningPath" :today-missions="todayMissions" />

    <SpeakingTeachingBlocks :blocks="teachingBlocks" />

    <SpeakingGuidedPractice
      :current-task="currentTask"
      :current-activity-kind="currentActivityKind"
      :activity-instructions="currentActivityInstructions"
    />

    <SpeakingTaskScreen
      :current-task="currentTask"
      :current-activity-title="currentActivityTitle"
      :activity-instructions="currentActivityInstructions"
      :expected-outcome="expectedOutcome"
      :live-execution-ready="liveExecutionReady"
      :can-continue="canContinueActivity"
      :advancing="advancing"
      :preparing-live="preparingLive"
      @continue-activity="$emit('continue-activity')"
      @talk-alex="$emit('talk-alex')"
    />

    <!-- Study / non-task continue surface -->
    <v-card
      v-if="canContinueActivity && !currentTask && !liveExecutionReady"
      class="glass-card pa-5 mb-5"
      variant="flat"
    >
      <div class="text-subtitle-1 font-weight-bold mb-2">
        {{ currentActivityTitle || t('student.languages.speakingJourney.lesson.studyStep') }}
      </div>
      <p v-if="currentActivityInstructions" class="text-body-2 mb-4" dir="auto">
        {{ currentActivityInstructions }}
      </p>
      <v-btn
        color="primary"
        class="em-btn em-btn--primary"
        :loading="advancing"
        prepend-icon="mdi-page-next"
        @click="$emit('continue-activity')"
      >
        {{ t('student.languages.speakingJourney.actions.continue') }}
      </v-btn>
    </v-card>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import SpeakingMissionHeader from './SpeakingMissionHeader.vue'
import SpeakingLessonProgress from './SpeakingLessonProgress.vue'
import SpeakingMissionTimeline from './SpeakingMissionTimeline.vue'
import SpeakingTeachingBlocks from './SpeakingTeachingBlocks.vue'
import SpeakingGuidedPractice from './SpeakingGuidedPractice.vue'
import SpeakingTaskScreen from './SpeakingTaskScreen.vue'

defineProps({
  lessonTitle: { type: String, default: '' },
  focusLabel: { type: String, default: '' },
  focusReason: { type: String, default: '' },
  planSummary: { type: String, default: '' },
  officialCefr: { type: String, default: '' },
  currentMission: { type: Object, default: null },
  nextMission: { type: Object, default: null },
  currentTask: { type: Object, default: null },
  attempt: { type: Object, default: null },
  objectives: { type: Array, default: () => [] },
  expectedOutcome: { type: String, default: '' },
  learningPath: { type: Array, default: () => [] },
  todayMissions: { type: Array, default: () => [] },
  teachingBlocks: { type: Array, default: () => [] },
  currentActivityTitle: { type: String, default: '' },
  currentActivityInstructions: { type: String, default: '' },
  currentActivityKind: { type: String, default: '' },
  activitiesTotal: { type: Number, default: 0 },
  activitiesCompleted: { type: Number, default: 0 },
  activitiesRemaining: { type: Number, default: 0 },
  liveExecutionReady: { type: Boolean, default: false },
  canContinueActivity: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  preparingLive: { type: Boolean, default: false },
})

defineEmits(['continue-activity', 'talk-alex'])

const { t } = useI18n()
</script>
