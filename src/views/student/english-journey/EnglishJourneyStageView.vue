<template>
  <JourneyShell>
    <template v-if="loading && !stage">
      <v-skeleton-loader type="article" />
    </template>

    <JourneyEmptyState
      v-else-if="!stage"
      icon="mdi-lock-outline"
      :title="t('student.englishJourney.stage.lockedHint')"
      :action-label="t('student.englishJourney.session.backHome')"
      :action-to="homeTo"
    />

    <StageDetailPanel
      v-else
      :stage="stage"
      :sections="sections"
      :can-start="canStart"
      :starting="starting"
      @start="onStart"
      @review="goReview"
    />

    <template #sidebar>
      <AiTeacherSidebar
        :mission="teacherSession?.mission || null"
        :energy="teacherSession?.energy || null"
        :confidence="averageConfidence"
        :next-milestone="nextStage?.display_name || ''"
      />
    </template>
  </JourneyShell>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useEnglishJourney } from '../../../composables/useEnglishJourney.js'
import { ROUTES } from '../../../constants/app.js'
import JourneyShell from '../../../components/english-journey/JourneyShell.vue'
import StageDetailPanel from '../../../components/english-journey/StageDetailPanel.vue'
import AiTeacherSidebar from '../../../components/english-journey/AiTeacherSidebar.vue'
import JourneyEmptyState from '../../../components/english-journey/JourneyEmptyState.vue'

const props = defineProps({
  grammarId: { type: String, required: true },
})

const { t } = useI18n()
const router = useRouter()
const homeTo = ROUTES.STUDENT_ENGLISH_JOURNEY

const {
  loading,
  starting,
  teacherSession,
  averageConfidence,
  nextStage,
  stageById,
  canOpenStage,
  canStartSessionFor,
  loadJourney,
  startTodaysSession,
  hydrateSession,
} = useEnglishJourney()

const stage = computed(() => stageById(props.grammarId))
const sections = computed(() => teacherSession.value?.sections || [])
const canStart = computed(() => canStartSessionFor(stage.value))

async function onStart() {
  await startTodaysSession({ navigate: true })
}

function goReview() {
  router.push(ROUTES.STUDENT_ENGLISH_JOURNEY_REVIEW)
}

watch(
  () => [props.grammarId, stage.value],
  () => {
    if (stage.value && !canOpenStage(stage.value)) {
      router.replace(ROUTES.STUDENT_ENGLISH_JOURNEY)
    }
  },
)

onMounted(async () => {
  hydrateSession()
  await loadJourney()
  if (stage.value && !canOpenStage(stage.value)) {
    router.replace(ROUTES.STUDENT_ENGLISH_JOURNEY)
  }
})
</script>
