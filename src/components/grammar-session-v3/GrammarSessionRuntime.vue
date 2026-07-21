<template>
  <div class="grammar-session">
    <SessionHeader
      :topic="lesson.grammar_target || lesson.lesson_title || ''"
      :cefr="cefr"
      :kicker="t('student.grammarSession.header.kicker')"
      :remaining-minutes="remainingMinutes"
      :progress-percent="progressPercent"
      :voice-state="teacherVoiceState"
      @exit="onExit"
    />

    <TeacherPresencePanel
      :teacher-name="teacherName"
      :teacher-focus="teacherFocus"
      :teacher-mood="teacherMood"
      :teacher-message="teacherMessage"
      :presence-state="presenceState"
    />

    <SessionTimeline
      :stages="stages"
      :current-stage="currentStage"
      :completed-stages="completedStages"
      :visited-stages="visitedStages"
      @select="onSelectStage"
    />

    <StageTransition :stage-key="stageTransitionKey">
      <component
        :is="stageComponent"
        :lesson="lesson"
        :skills="skills"
        :teacher-name="teacherName"
        :teacher-message="teacherMessage"
        :voice-state="teacherVoiceState"
        :teaching-cards="teachingCards"
        :teach-card-index="teachCardIndex"
        :current-teach-card="currentTeachCard"
        :all-teach-cards-seen="allTeachCardsSeen"
        @ask="openAsk"
        @next-card="onNextTeachCard"
      />
    </StageTransition>

    <SessionFooter
      :stage-index="stageIndex"
      :total-stages="totalStages"
      :elapsed-seconds="elapsedSeconds"
      :can-back="canGoBack"
      :can-next="footerCanNext"
      :is-last="isLastStage"
      :loading="completing || thinking"
      :primary-label="primaryLabel"
      @back="back"
      @continue="onContinue"
      @finish="onFinish"
    />

    <AskTeacherDrawer
      :open="askOpen"
      :draft="askDraft"
      :error="askError"
      :loading="thinking"
      @update:draft="onAskDraft"
      @close="closeAsk"
      @submit="askTeacher()"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, toRef, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGrammarSessionRuntime } from '../../composables/useGrammarSessionRuntime.js'
import { useGrammarTeacherExperience } from '../../composables/useGrammarTeacherExperience.js'
import SessionHeader from '../ai-session/SessionHeader.vue'
import SessionTimeline from '../ai-session/SessionTimeline.vue'
import SessionFooter from '../ai-session/SessionFooter.vue'
import StageTransition from '../ai-session/StageTransition.vue'
import TeacherPresencePanel from './teacher/TeacherPresencePanel.vue'
import AskTeacherDrawer from './teacher/AskTeacherDrawer.vue'
import WelcomeStage from './stages/WelcomeStage.vue'
import MissionStage from './stages/MissionStage.vue'
import LearnStage from './stages/LearnStage.vue'
import PracticeStage from './stages/PracticeStage.vue'
import SpeakingStage from './stages/SpeakingStage.vue'
import WritingStage from './stages/WritingStage.vue'
import ReflectionStage from './stages/ReflectionStage.vue'
import CompleteStage from './stages/CompleteStage.vue'

const props = defineProps({
  lesson: { type: Object, required: true },
  skills: { type: Array, default: () => [] },
  cefr: { type: String, default: '' },
  completing: { type: Boolean, default: false },
})

const emit = defineEmits(['exit', 'finish'])
const { t } = useI18n()

const {
  stages,
  currentStage,
  visitedStages,
  completedStages,
  elapsedSeconds,
  teacherVoiceState,
  listeningState,
  speakingState,
  stageIndex,
  totalStages,
  progressPercent,
  canGoBack,
  canGoNext,
  isLastStage,
  dirty,
  memory,
  bindLesson,
  next,
  back,
  goToStage,
  completeSession,
  setTeacherContext,
  estimatedRemainingMinutes,
} = useGrammarSessionRuntime()

const lessonRef = toRef(props, 'lesson')

const {
  teacherName,
  teacherFocus,
  teacherMood,
  teacherMessage,
  thinking,
  presenceState,
  askOpen,
  askDraft,
  askError,
  teachingCards,
  teachCardIndex,
  currentTeachCard,
  allTeachCardsSeen,
  bootstrap,
  openAsk,
  closeAsk,
  askTeacher,
  advanceTeachCard,
} = useGrammarTeacherExperience({
  lesson: lessonRef,
  currentStage,
  teacherVoiceState,
  listeningState,
  speakingState,
  setTeacherContext,
  memory,
})

function onAskDraft(value) {
  askDraft.value = value
}

const STAGE_MAP = {
  WELCOME: WelcomeStage,
  MISSION: MissionStage,
  LEARN: LearnStage,
  PRACTICE: PracticeStage,
  SPEAKING: SpeakingStage,
  WRITING: WritingStage,
  REFLECTION: ReflectionStage,
  COMPLETE: CompleteStage,
}

const stageComponent = computed(() => STAGE_MAP[currentStage.value] || WelcomeStage)

const stageTransitionKey = computed(() => {
  if (currentStage.value === 'LEARN') {
    return `LEARN-${teachCardIndex.value}`
  }
  return currentStage.value
})

const remainingMinutes = computed(() =>
  estimatedRemainingMinutes(props.lesson?.estimated_minutes),
)

const footerCanNext = computed(() => {
  if (currentStage.value === 'LEARN' && !allTeachCardsSeen.value) return true
  return canGoNext.value
})

const primaryLabel = computed(() => {
  if (isLastStage.value) return t('student.grammarSession.controls.finish')
  if (currentStage.value === 'LEARN' && !allTeachCardsSeen.value) {
    return t('student.grammarTeacher.cards.next')
  }
  if (currentStage.value === 'REFLECTION') {
    return t('student.grammarSession.controls.toComplete')
  }
  return t('student.grammarSession.controls.continue')
})

function confirmLeave() {
  if (!dirty.value) return true
  return window.confirm(t('student.grammarSession.leaveConfirm'))
}

function onNextTeachCard() {
  advanceTeachCard()
}

function onContinue() {
  if (currentStage.value === 'LEARN' && !allTeachCardsSeen.value) {
    advanceTeachCard()
    return
  }
  next()
}

function onSelectStage(stage) {
  goToStage(stage)
}

function onExit() {
  if (!confirmLeave()) return
  emit('exit')
}

function onFinish() {
  completeSession()
  emit('finish')
}

function onBeforeUnload(e) {
  if (!dirty.value) return
  e.preventDefault()
  e.returnValue = ''
}

onMounted(() => {
  bindLesson(props.lesson)
  bootstrap()
  window.addEventListener('beforeunload', onBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', onBeforeUnload)
})

watch(
  () => props.lesson?.lesson_id,
  (id, prev) => {
    if (id && id !== prev) {
      bindLesson(props.lesson)
      bootstrap()
    }
  },
)

onBeforeRouteLeave((_to, _from, nextLeave) => {
  nextLeave(confirmLeave())
})
</script>

<style scoped>
.grammar-session {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 920px;
  margin-inline: auto;
}
</style>
