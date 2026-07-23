<template>
  <div>
    <v-alert v-if="combinedError" type="warning" variant="tonal" class="mb-4 rounded-lg">{{ combinedError }}</v-alert>

    <LearningLoader
      v-if="phase === 'generating'"
      :title="t('student.languages.writingJourney.practice.generating')"
    />

    <v-card v-else-if="phase === 'error' && !lesson" class="intro-card pa-8 text-center" variant="flat">
      <v-alert type="error" variant="tonal" class="mb-4">{{ combinedError }}</v-alert>
      <v-btn color="secondary" variant="flat" @click="startLesson">{{ t('student.languages.common.retry') }}</v-btn>
    </v-card>

    <v-card v-else-if="phase === 'idle' && !lesson" class="intro-card pa-8 pa-md-10 text-center" variant="flat">
      <div class="intro-icon mb-4">✍️</div>
      <h3 class="text-h5 font-weight-bold mb-2">{{ t('student.languages.writingJourney.practice.introTitle') }}</h3>
      <p class="text-body-1 text-medium-emphasis mb-6 mx-auto intro-body">{{ t('student.languages.writingJourney.practice.introBody') }}</p>
      <v-btn
        color="secondary"
        variant="flat"
        size="x-large"
        :loading="phase === 'generating'"
        prepend-icon="mdi-auto-fix"
        class="px-10"
        @click="startLesson"
      >
        {{ t('student.languages.writingJourney.practice.generate') }}
      </v-btn>
    </v-card>

    <template v-else-if="lesson">
      <WritingProgressPanel
        v-if="completed"
        :progress="lessonProgress"
        :next-lesson="nextLesson"
        @new-lesson="onNewLesson"
      />

      <template v-else>
        <ListeningMissionCard
          :title="t('student.languages.writingJourney.practice.missionTitle')"
          icon="mdi-pencil-outline"
          :subtitle="lesson.mission_title || lesson.title"
          :focus-title="t('student.languages.writingJourney.practice.todaysGoal')"
          :focus-items="goalItems"
          :why-title="t('student.languages.writingJourney.practice.contextTitle')"
          :why-text="lesson.writing_context || lesson.prompt"
          :meta-rows="missionMeta"
          :reward-label="t('student.languages.writingJourney.practice.expectedOutput')"
          :reward-text="lesson.expected_output"
        />

        <v-card class="glass-card pa-6 mb-4" variant="flat">
          <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.practice.promptTitle') }}</div>
          <p class="text-body-1 mb-4" dir="ltr">{{ lesson.prompt }}</p>

          <div v-if="lesson.instructions?.length" class="mb-4">
            <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.practice.instructions') }}</div>
            <ul class="instruction-list">
              <li v-for="(line, idx) in lesson.instructions" :key="idx" dir="ltr">{{ line }}</li>
            </ul>
          </div>

          <div v-if="lesson.checklist?.length" class="mb-4">
            <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.writingJourney.practice.successCriteria') }}</div>
            <ul class="instruction-list">
              <li v-for="(line, idx) in lesson.checklist" :key="`c-${idx}`" dir="ltr">{{ line }}</li>
            </ul>
          </div>

          <v-textarea
            v-model="draftText"
            :label="t('student.languages.writingJourney.practice.editorLabel')"
            rows="10"
            auto-grow
            dir="ltr"
            variant="outlined"
            class="mt-2"
          />
          <div class="text-caption text-medium-emphasis mt-2">
            {{ t('student.languages.writingJourney.practice.counters', { words: localWordCount, min: lesson.min_words, max: lesson.max_words }) }}
            <span v-if="revisionNumber > 0" class="ms-2">
              · {{ t('student.languages.writingJourney.practice.revision', { n: revisionNumber }) }}
            </span>
          </div>

          <v-alert
            v-if="validationMessage"
            type="warning"
            variant="tonal"
            density="comfortable"
            class="mt-3 rounded-lg"
            dir="ltr"
          >
            {{ validationMessage }}
          </v-alert>

          <div class="d-flex flex-wrap gap-3 mt-4">
            <v-btn
              color="secondary"
              variant="flat"
              size="large"
              :loading="submitting"
              :disabled="!canSubmitDraft"
              @click="onSubmitDraft"
            >
              {{ revisionNumber > 0 ? t('student.languages.writingJourney.practice.resubmit') : t('student.languages.writingJourney.practice.submitDraft') }}
            </v-btn>
            <v-btn
              v-if="readyToComplete && !completed"
              color="success"
              variant="flat"
              size="large"
              :loading="submitting"
              :disabled="!canSubmitDraft"
              @click="onComplete"
            >
              {{ t('student.languages.writingJourney.practice.complete') }}
            </v-btn>
          </div>
        </v-card>

        <WritingEvaluationPanel
          :has-evaluation="hasEvaluation"
          :dimensions="dimensions"
          :success-criteria="successCriteria"
          :strengths="strengths"
          :improvements="improvements"
          :ready-to-complete="readyToComplete"
        />

        <WritingTeacherAnalysisPanel :analysis="educationalAnalysis" />

        <WritingCoachPanel
          :has-coach="hasCoach"
          :encouragement="encouragement"
          :main-issue="mainIssue"
          :why-it-matters="whyItMatters"
          :mission="mission"
          :before-example="beforeExample"
          :after-example="afterExample"
        />
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ListeningMissionCard from './ListeningMissionCard.vue'
import LearningLoader from './LearningLoader.vue'
import WritingCoachPanel from './WritingCoachPanel.vue'
import WritingEvaluationPanel from './WritingEvaluationPanel.vue'
import WritingTeacherAnalysisPanel from './WritingTeacherAnalysisPanel.vue'
import WritingProgressPanel from './WritingProgressPanel.vue'
import { useWritingLesson } from '../../composables/useWritingLesson.js'
import { useWritingRevision } from '../../composables/useWritingRevision.js'
import { useWritingCoach } from '../../composables/useWritingCoach.js'
import { useWritingEvaluation } from '../../composables/useWritingEvaluation.js'
import { countWritingWords, validateWritingText } from '../../utils/languageValidation.js'
import { celebrateBig } from '../../composables/useCelebrate.js'

const props = defineProps({
  activeGoalId: { type: String, default: 'travel' },
})

const emit = defineEmits(['lesson-ready', 'completed', 'error'])

const { t } = useI18n()
const { lesson, phase, error: lessonError, generate, reset: resetLesson } = useWritingLesson()
const {
  draftText,
  submitting,
  error: revisionError,
  lastTurn,
  revisionNumber,
  completed,
  submitDraft,
  resetRevision,
} = useWritingRevision(() => lesson.value?.content_item_id)

const {
  hasCoach,
  encouragement,
  mainIssue,
  whyItMatters,
  mission,
  beforeExample,
  afterExample,
  nextLesson,
} = useWritingCoach(lastTurn)

const {
  hasEvaluation,
  readyToComplete,
  dimensions,
  successCriteria,
  strengths,
  improvements,
  lessonProgress,
  educationalAnalysis,
} = useWritingEvaluation(lastTurn)

const combinedError = computed(() => lessonError.value || revisionError.value)

const localWordCount = computed(() => countWritingWords(draftText.value))

const goalItems = computed(() => {
  if (!lesson.value) return []
  const items = lesson.value.learning_outcomes?.length
    ? lesson.value.learning_outcomes
    : lesson.value.success_criteria
  return items || []
})

const missionMeta = computed(() => {
  if (!lesson.value) return []
  return [
    { label: t('student.languages.writingJourney.practice.metaLevel'), value: lesson.value.official_cefr || '—' },
    { label: t('student.languages.writingJourney.practice.metaGoal'), value: lesson.value.goal || '—' },
    { label: t('student.languages.writingJourney.practice.metaWords'), value: `${lesson.value.min_words}–${lesson.value.max_words}` },
  ]
})

const validationMessage = computed(() => {
  if (!lesson.value || !draftText.value.trim()) return ''
  const check = validateWritingText(draftText.value, { minWords: lesson.value.min_words, minSentences: 0 })
  return check.ok ? '' : check.message
})

const canSubmitDraft = computed(() => Boolean(lesson.value && draftText.value.trim()))
const staleLessonError = 'انتهت صلاحية درس الكتابة. أنشئ درساً جديداً وحاول مرة ثانية.'

async function startLesson() {
  try {
    const data = await generate({ goal: props.activeGoalId })
    resetRevision()
    emit('lesson-ready', data)
  } catch (err) {
    emit('error', err)
  }
}

async function onSubmitDraft() {
  try {
    await submitDraft({ completeIfReady: false })
  } catch (err) {
    if (err?.response?.status === 404) {
      resetLesson()
      resetRevision()
      emit('error', new Error(staleLessonError))
      return
    }
    emit('error', err)
  }
}

async function onComplete() {
  try {
    const result = await submitDraft({ completeIfReady: true })
    if (result?.completed) {
      celebrateBig()
      emit('completed', { lesson: lesson.value, turn: result, progress: result.lesson_progress })
    }
  } catch (err) {
    if (err?.response?.status === 404) {
      resetLesson()
      resetRevision()
      emit('error', new Error(staleLessonError))
      return
    }
    emit('error', err)
  }
}

function onNewLesson() {
  resetLesson()
  resetRevision()
}

defineExpose({ startLesson })
</script>

<style scoped>
.intro-card {
  border-radius: 20px;
}
.intro-icon {
  font-size: 3rem;
  line-height: 1;
}
.intro-body {
  max-width: 36rem;
}
.instruction-list {
  margin: 0;
  padding-inline-start: 1.25rem;
}
.instruction-list li + li {
  margin-top: 0.35rem;
}
</style>
