<template>
  <div class="page-container">
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

    <template v-if="starting || (!activeLesson && loading)">
      <v-skeleton-loader type="article, article, article" />
    </template>

    <AppEmptyState
      v-else-if="!activeLesson"
      icon="mdi-book-open-blank-variant"
      :title="t('student.grammarV2.errors.lesson')"
      :description="actionError || undefined"
      :action-label="t('student.grammarV2.review.backHome')"
      :action-to="homeTo"
    />

    <GrammarLessonPage
      v-else
      :lesson="activeLesson"
      :cefr="sessionCefr"
      :finishing="completing"
      @back="goHome"
      @retry="restartLesson"
      @finish="finishLesson"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGrammarEngineHome } from '../../../composables/useGrammarEngineHome.js'
import { hasCanonicalGrammarLessonContent } from '../../../composables/useGrammarLessonSession.js'
import GrammarLessonPage from '../../../components/grammar-lesson-v4/GrammarLessonPage.vue'
import AppEmptyState from '../../../components/ui/AppEmptyState.vue'
import { ROUTES } from '../../../constants/app.js'

const props = defineProps({
  grammarId: { type: String, required: true },
})

const { t } = useI18n()
const router = useRouter()
const homeTo = ROUTES.STUDENT_GRAMMAR

const {
  loading,
  starting,
  completing,
  actionError,
  activeLesson,
  hasActiveLesson,
  progress,
  stageById,
  canOpenStage,
  hydrate,
  loadHome,
  startCurrentLesson,
  finishLesson,
  clearLesson,
} = useGrammarEngineHome()

const stage = computed(() => stageById(props.grammarId))
const sessionCefr = computed(
  () => progress.value?.cefr_label || stage.value?.cefr || '',
)

function goHome() {
  router.push(ROUTES.STUDENT_GRAMMAR)
}

function clearActionError() {
  actionError.value = ''
}

function lessonRouteTarget(lesson) {
  return lesson?.grammar_id || lesson?.grammar_target || ''
}

function canReuseActiveLesson() {
  if (!hasCanonicalGrammarLessonContent(activeLesson.value)) return false
  if (props.grammarId === 'current') return true
  const target = lessonRouteTarget(activeLesson.value)
  return !target || target === props.grammarId
}

async function restartLesson() {
  clearLesson()
  await startCurrentLesson({
    grammarId: props.grammarId === 'current' ? null : props.grammarId,
    navigate: false,
  })
}

onMounted(async () => {
  hydrate()

  if (hasActiveLesson.value && canReuseActiveLesson()) {
    loadHome()
    return
  }
  if (hasActiveLesson.value) {
    clearLesson()
  }

  await loadHome()

  const s = props.grammarId === 'current' ? null : stageById(props.grammarId)
  if (s && !canOpenStage(s)) {
    router.replace(ROUTES.STUDENT_GRAMMAR)
    return
  }

  if (!hasActiveLesson.value) {
    await startCurrentLesson({
      grammarId: props.grammarId === 'current' ? null : props.grammarId,
      navigate: false,
    })
  }
})
</script>
