<template>
  <div>
    <v-alert v-if="submitError" type="warning" variant="tonal" class="mb-4 rounded-lg">{{ submitError }}</v-alert>

    <ListeningAcquisitionCard
      v-if="phase === 'loading' || phase === 'pending' || phase === 'unavailable'"
      :acquisition="acquisition"
      :phase="phase"
      @retry="onRetry"
    />

    <v-card v-else-if="phase === 'idle' && !lessonBundle" class="intro-card pa-8 pa-md-10 text-center" variant="flat">
      <div class="intro-icon mb-4">🎧</div>
      <h3 class="text-h5 font-weight-bold mb-2">{{ introTitle }}</h3>
      <p class="text-body-1 text-medium-emphasis mb-6 mx-auto intro-body">{{ introBody }}</p>
      <v-btn
        color="secondary"
        variant="flat"
        size="x-large"
        :loading="phase === 'loading'"
        prepend-icon="mdi-play"
        class="px-10"
        @click="startLesson"
      >
        {{ startLabel }}
      </v-btn>
    </v-card>

    <template v-else-if="lessonBundle">
      <ListeningMissionCard
        v-if="!submitResponse"
        :title="t('student.languages.coach.ux.mission.title')"
        icon="mdi-target"
        :subtitle="lessonBundle.narrative?.coach_summary || lessonBundle.lesson_title"
        :focus-title="t('student.languages.coach.ux.mission.todayWePractice')"
        :focus-items="lessonBundle.narrative?.student_focus || []"
        :why-title="t('student.languages.coach.ux.mission.whyTitle')"
        :why-text="lessonBundle.narrative?.why_this_lesson || ''"
        :meta-rows="missionMeta"
        :reward-label="t('student.languages.coach.ux.mission.rewardLabel')"
        :reward-text="lessonBundle.narrative?.reward || ''"
      />

      <v-card
        v-if="!submitResponse && lessonBundle.narrative?.next_after_this"
        class="glass-card pa-5 mb-4"
        variant="flat"
      >
        <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.listeningJourney.practice.whatNextTitle') }}</div>
        <p class="text-body-2 text-medium-emphasis mb-0">{{ lessonBundle.narrative.next_after_this }}</p>
      </v-card>

      <v-card class="glass-card pa-6 mb-4" variant="flat">
        <p v-if="playback.instructions" class="text-body-2 text-medium-emphasis mb-3" dir="ltr">{{ playback.instructions }}</p>
        <AudioVisualizer
          v-if="playback.audio_available && playback.audio_url && !audioBroken"
          :src="playback.audio_url"
          @error="audioBroken = true"
        />
        <v-alert v-else type="info" variant="tonal" density="comfortable">
          {{ t('student.languages.listening.audioUnavailableBody') }}
        </v-alert>
        <div class="text-caption text-medium-emphasis mt-3 text-end">
          {{ t('student.languages.listeningJourney.practice.answered', { n: answeredCount, total: questions.length }) }}
        </div>
      </v-card>

      <v-card v-if="!submitResponse" class="glass-card pa-6" variant="flat">
        <LanguageMcqForm v-model:answers="answers" :questions="questions" />
        <v-btn
          color="secondary"
          variant="flat"
          size="large"
          class="mt-5"
          block
          :loading="submitting"
          :disabled="!canSubmit"
          @click="submit"
        >
          {{ t('student.languages.common.submitAnswers') }}
        </v-btn>
      </v-card>

      <template v-else>
        <v-card class="result-card pa-6 mb-4" variant="flat">
          <h3 class="text-h5 font-weight-bold mb-1">{{ afterLesson.headline || t('student.languages.coach.ux.lessonResult.greatWork') }}</h3>
          <p class="text-body-1 text-medium-emphasis mb-5">{{ afterLesson.summary }}</p>

          <div v-if="afterLesson.improved?.length" class="mb-4">
            <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.coach.ux.lessonResult.todayImproved') }}</div>
            <div v-for="(line, idx) in afterLesson.improved" :key="idx" class="result-row d-flex align-center gap-2 py-1">
              <v-icon color="success" size="20">mdi-check-circle</v-icon>
              <span class="text-body-1">{{ line }}</span>
            </div>
          </div>

          <div v-if="afterLesson.needs_practice?.length" class="mb-4">
            <div class="text-body-2 font-weight-bold mb-2">{{ t('student.languages.coach.ux.lessonResult.needsPractice') }}</div>
            <div v-for="(text, idx) in afterLesson.needs_practice" :key="idx" class="result-row d-flex align-center gap-2 py-1">
              <v-icon color="medium-emphasis" size="20">mdi-circle-outline</v-icon>
              <span class="text-body-1 text-medium-emphasis">{{ text }}</span>
            </div>
          </div>

          <div v-if="afterLesson.next_lesson_teaser" class="next-lesson-hint pt-3">
            <div class="text-body-2 font-weight-bold mb-1">{{ t('student.languages.coach.ux.lessonResult.nextLesson') }}</div>
            <p class="text-body-1 mb-0">{{ afterLesson.next_lesson_teaser }}</p>
          </div>
        </v-card>

        <v-card class="glass-card pa-6" variant="flat">
          <div class="d-flex flex-wrap gap-3">
            <v-btn color="secondary" variant="flat" size="large" @click="retry">{{ t('student.languages.common.retry') }}</v-btn>
            <v-btn color="secondary" variant="tonal" size="large" @click="startLesson">{{ t('student.languages.listeningJourney.practice.nextClip') }}</v-btn>
          </div>
        </v-card>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import LanguageMcqForm from './LanguageMcqForm.vue'
import AudioVisualizer from './AudioVisualizer.vue'
import ListeningMissionCard from './ListeningMissionCard.vue'
import ListeningAcquisitionCard from './ListeningAcquisitionCard.vue'
import { submitListeningLesson } from '../../api/language.js'
import { useListeningAcquisition } from '../../composables/useListeningAcquisition.js'
import { buildSubmitAnswers } from '../../composables/useLanguageGate.js'
import { getErrorMessage } from '../../api/client.js'
import { celebrate, celebrateBig } from '../../composables/useCelebrate.js'

const props = defineProps({
  activeLessonId: { type: Number, default: null },
  activeLessonLifecycle: { type: String, default: null },
})

const emit = defineEmits(['submitted', 'before-submit', 'lesson-ready'])

const { t } = useI18n()

const {
  bundle: lessonBundle,
  acquisition,
  phase,
  start,
  retry: retryAcquisition,
  reset,
  stopPolling,
} = useListeningAcquisition()

const answers = ref({})
const submitting = ref(false)
const submitResponse = ref(null)
const submitError = ref('')
const audioBroken = ref(false)

const playback = computed(() => lessonBundle.value?.playback || {})
const questions = computed(() => playback.value.questions || [])
const afterLesson = computed(() => submitResponse.value?.bundle?.after_lesson || {})

const canResume = computed(() => {
  const id = props.activeLessonId
  const life = props.activeLessonLifecycle
  return Boolean(id && life && ['reserved', 'started'].includes(life))
})

const introTitle = computed(() =>
  canResume.value
    ? t('student.languages.listeningJourney.practice.resume')
    : t('student.languages.listeningJourney.practice.introTitle'),
)

const introBody = computed(() =>
  canResume.value
    ? t('student.languages.listeningJourney.practice.resumeHint')
    : t('student.languages.listeningJourney.practice.introBody'),
)

const startLabel = computed(() =>
  canResume.value
    ? t('student.languages.listeningJourney.practice.resume')
    : t('student.languages.listeningJourney.practice.start'),
)

const answeredCount = computed(() =>
  questions.value.filter((q) => answers.value[q.id] != null).length,
)

const canSubmit = computed(() =>
  questions.value.length &&
  questions.value.every((q) => answers.value[q.id] !== undefined && answers.value[q.id] !== null),
)

const missionMeta = computed(() => {
  if (!lessonBundle.value) return []
  return [
    { label: t('student.languages.coach.ux.mission.metaLevel'), value: lessonBundle.value.lesson_level || '—' },
    { label: t('student.languages.coach.ux.mission.metaOfficial'), value: lessonBundle.value.official_level || '—' },
    { label: t('student.languages.coach.ux.mission.metaGoal'), value: lessonBundle.value.lesson_goal?.label || '—' },
    { label: t('student.languages.coach.ux.mission.metaSituation'), value: lessonBundle.value.situation || '—' },
  ].filter((row) => row.value && row.value !== '—')
})

watch(lessonBundle, (b) => {
  if (b) emit('lesson-ready', b)
})

async function startLesson() {
  submitError.value = ''
  submitResponse.value = null
  answers.value = {}
  audioBroken.value = false
  await start({
    resumeLessonId: canResume.value ? props.activeLessonId : null,
  })
}

async function onRetry() {
  submitError.value = ''
  await retryAcquisition()
}

async function submit() {
  if (!lessonBundle.value || submitting.value) return
  submitting.value = true
  submitError.value = ''
  emit('before-submit')
  try {
    submitResponse.value = await submitListeningLesson(
      lessonBundle.value.lesson_id,
      buildSubmitAnswers(answers.value),
    )
    lessonBundle.value = submitResponse.value.bundle
    if (submitResponse.value?.score_percent >= 100) celebrateBig()
    else if (submitResponse.value?.passed) celebrate()
    emit('submitted', submitResponse.value)
  } catch (e) {
    submitError.value = getErrorMessage(e, t('student.languages.listeningJourney.practice.errors.submit'))
  } finally {
    submitting.value = false
  }
}

function retry() {
  submitResponse.value = null
  answers.value = {}
}

onBeforeUnmount(() => {
  stopPolling()
})

defineExpose({ startLesson, reset })
</script>

<style scoped>
.intro-card {
  border-radius: 24px;
}
.intro-icon {
  font-size: 3rem;
  line-height: 1;
}
.intro-body {
  max-width: 28rem;
}
.result-card {
  border-radius: 20px;
  background: linear-gradient(
    145deg,
    rgba(var(--v-theme-success), 0.08),
    rgba(var(--v-theme-surface), 1)
  );
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.next-lesson-hint {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}
</style>
