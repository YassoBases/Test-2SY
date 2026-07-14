<template>
  <div class="lesson-page slide-up-enter-active">
    <v-card class="glass-card pa-3 pa-md-4 mb-4 lesson-course-nav" variant="flat">
      <div class="lesson-course-nav__row d-flex align-center flex-wrap gap-3">
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-arrow-right"
          :to="courseBackRoute"
          class="lesson-course-nav__back"
        >
          {{ t('student.lesson.nav.backToLessons') }}
        </v-btn>
        <v-spacer class="d-none d-sm-flex" />
        <div class="lesson-course-nav__arrows d-flex gap-2">
          <v-btn
            variant="outlined"
            size="small"
            prepend-icon="mdi-chevron-right"
            :disabled="!prevLesson"
            @click="goToLesson(prevLesson?.id)"
          >
            {{ t('student.lesson.nav.previous') }}
          </v-btn>
          <v-btn
            variant="outlined"
            size="small"
            append-icon="mdi-chevron-left"
            :disabled="!nextLesson"
            @click="goToLesson(nextLesson?.id)"
          >
            {{ t('student.lesson.nav.next') }}
          </v-btn>
        </div>
      </div>
    </v-card>

    <div v-if="!loadError" class="lesson-session-shell">
      <LessonSessionHeader
        :lesson-title="lesson.title"
        :teacher-name="lesson.teacherName"
        :teacher-image-url="lesson.teacherImageUrl"
        :subject="lesson.subject"
        :grade="lesson.grade"
        :lesson-position="lessonPositionLabel"
        :progress-percent="sessionProgressPercent"
        :next-action="headerNextAction"
        :pdf-url="lesson.pdfUrl"
        :action-loading="isRegeneratingQuiz"
        @action="runHeaderAction"
      />
      <LessonStepStrip :steps="sessionSteps" @select="onStepSelect" />
      <div class="lesson-session-layout">
        <div class="lesson-session-layout__content">
          <LessonLearnFlow
            ref="learnFlowRef"
            :teacher-name="lesson.teacherName"
            :teacher-image-url="lesson.teacherImageUrl"
            :video-src="lessonVideoSrc"
            :pdf-url="lesson.has_pdf && lesson.pdfUrl ? mediaUrl(lesson.pdfUrl) : ''"
            :preview="lesson.preview || ''"
            :summary="lesson.lessonSummary || []"
            :keywords="lesson.keywords || []"
            :has-video="lesson.has_video"
            :has-pdf="lesson.has_pdf"
            :has-ai-chat="lesson.has_ai_chat"
            :chat-disabled="!lesson.has_ai_chat || lesson.ai_processing"
            :chat-disabled-hint="chatDisabledHint"
            :continue-action="learnContinueAction"
            @video-timeupdate="onVideoTimeupdate"
            @pdf-opened="onPdfOpened"
            @pdf-progress="onPdfProgress"
            @continue="runLearnContinue"
            @ask-teacher="openChatExperience"
            @concept-action="onConceptAction"
          />
        </div>

        <div class="lesson-session-layout__assistant">
          <v-card
            ref="sessionToolsRef"
            class="glass-card lesson-session-tools-card overflow-hidden"
            variant="flat"
          >
            <v-tabs v-model="sessionTab" color="secondary" grow class="lesson-tabs">
              <v-tab value="chat">
                <v-icon start size="18">mdi-message-text</v-icon>
                {{ t('student.lesson.tabs.askTeacher') }}
              </v-tab>
              <v-tab value="quiz">
                <v-icon start size="18">mdi-clipboard-check</v-icon>
                {{ t('student.lesson.tabs.quiz') }}
              </v-tab>
            </v-tabs>
            <v-divider class="opacity-10" />
            <v-window v-model="sessionTab" class="lesson-window">
              <v-window-item value="chat" class="tab-panel tab-panel--chat">
                <ChatPanel
                  ref="chatPanelRef"
                  v-model="chatInput"
                  :messages="messages"
                  :is-typing="isTyping"
                  :teacher-name="lesson.teacherName"
                  :teacher-image-url="lesson.teacherImageUrl"
                  :voice-tts-available="voiceTtsAvailable"
                  :voice-tts-message="voiceTtsMessage"
                  :clear-disabled="!messages.length || !lesson.has_ai_chat"
                  :clear-loading="isClearingChat"
                  :send-disabled="!lesson.has_ai_chat"
                  :status-notice="chatStatusNotice"
                  :status-loading="lesson.ai_processing && !lesson.has_ai_chat"
                  :status-error="!!lesson.ai_error && !lesson.has_ai_chat"
                  @send="onSend"
                  @voice="onVoice"
                  @clear="openClearDialog"
                />
              </v-window-item>
              <v-window-item value="quiz" class="tab-panel">
                <div class="lesson-sidebar pa-4 pa-md-5">
          <v-card class="glass-card learning-progress pa-5 mb-5" variant="flat">
            <div class="d-flex align-center justify-space-between gap-3 mb-3">
              <div>
                <span class="section-eyebrow mb-1">{{ t('student.lesson.progress.eyebrow') }}</span>
                <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.progress.sessionTitle') }}</h3>
              </div>
              <v-progress-circular
                :model-value="progressPercent"
                :size="58"
                :width="6"
                color="secondary"
              >
                <span class="text-caption font-weight-bold">{{ progressPercent }}%</span>
              </v-progress-circular>
            </div>
            <v-progress-linear
              :model-value="progressPercent"
              height="8"
              rounded
              color="secondary"
              bg-opacity="0.16"
              class="mb-4"
            />
            <div class="next-step mb-4">
              <v-icon color="secondary" size="22">{{ progressNextStep.icon }}</v-icon>
              <div class="next-step__copy">
                <span>{{ t('student.lesson.progress.nextStep') }}</span>
                <strong>{{ progressNextStep.text }}</strong>
              </div>
              <v-btn
                v-if="progressNextStep.action"
                size="small"
                color="secondary"
                variant="tonal"
                :loading="progressNextStep.action === 'regenerateQuiz' && isRegeneratingQuiz"
                :disabled="progressActionDisabled"
                @click="runProgressAction"
              >
                {{ progressNextStep.cta }}
              </v-btn>
            </div>
            <div class="progress-grid">
              <div class="progress-stat">
                <v-icon color="primary" size="18">mdi-message-question</v-icon>
                <strong>{{ studentQuestionCount }}</strong>
                <span>{{ t('student.lesson.progress.stats.questions') }}</span>
              </div>
              <div class="progress-stat">
                <v-icon color="secondary" size="18">mdi-clipboard-check</v-icon>
                <strong>{{ answeredCount }}/{{ quizTotal }}</strong>
                <span>{{ t('student.lesson.progress.stats.quiz') }}</span>
              </div>
              <div class="progress-stat">
                <v-icon color="error" size="18">mdi-alert-circle-outline</v-icon>
                <strong>{{ mistakeReview.length }}</strong>
                <span>{{ t('student.lesson.progress.stats.mistakes') }}</span>
              </div>
            </div>
          </v-card>

          <div class="mb-5">
            <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
              <v-icon color="secondary">mdi-message-star</v-icon>
              {{ t('student.lesson.feedback.title') }}
            </h3>
            <TransitionGroup name="feedback">
              <FeedbackCard
                v-for="fb in activeFeedback"
                :key="fb.id"
                :feedback="fb"
              />
            </TransitionGroup>
            <p v-if="!activeFeedback.length" class="text-caption text-medium-emphasis">
              {{ t('student.lesson.feedback.empty') }}
            </p>
          </div>

          <template v-if="lesson.quizQuestions?.length">
            <QuizResults
              :show="quizComplete"
              :correct-count="quizScore.correct"
              :total="lesson.quizQuestions.length"
              @retry="resetQuiz"
            />

            <v-card
              v-if="quizComplete"
              class="glass-card learning-plan pa-5 mb-4"
              variant="flat"
            >
              <div class="d-flex align-center justify-space-between gap-3 mb-4">
                <div>
                  <span class="section-eyebrow mb-1">{{ learningPlanLabel }}</span>
                  <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.plan.title') }}</h3>
                </div>
                <v-chip
                  size="small"
                  :color="mistakeReview.length ? 'warning' : 'success'"
                  variant="tonal"
                >
                  {{ mistakeReview.length ? t('student.lesson.plan.chip.review') : t('student.lesson.plan.chip.consolidate') }}
                </v-chip>
              </div>

              <div class="learning-plan__list">
                <div
                  v-for="item in learningPlanItems"
                  :key="item.id"
                  class="learning-plan__item"
                >
                  <v-avatar
                    :color="item.color"
                    variant="tonal"
                    size="36"
                    class="learning-plan__icon"
                  >
                    <v-icon size="20">{{ item.icon }}</v-icon>
                  </v-avatar>
                  <div class="learning-plan__copy">
                    <strong>{{ item.title }}</strong>
                    <span>{{ item.description }}</span>
                  </div>
                  <v-btn
                    v-if="item.action"
                    size="small"
                    :color="item.color"
                    variant="tonal"
                    :loading="learningPlanActionLoading(item.action)"
                    :disabled="learningPlanActionDisabled(item.action)"
                    @click="runLearningPlanAction(item.action)"
                  >
                    {{ item.cta }}
                  </v-btn>
                </div>
              </div>
            </v-card>

            <div v-if="!quizComplete">
              <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
                <v-icon color="primary">mdi-clipboard-check</v-icon>
                {{ t('student.lesson.quiz.title') }}
                <v-chip size="x-small" variant="tonal" color="primary">
                  {{ answeredCount }}/{{ lesson.quizQuestions.length }}
                </v-chip>
                <v-spacer />
                <v-tooltip :text="t('student.lesson.quiz.regenerateTooltip')" location="bottom">
                  <template #activator="{ props: tooltipProps }">
                    <v-btn
                      v-bind="tooltipProps"
                      icon="mdi-refresh"
                      size="small"
                      variant="tonal"
                      color="secondary"
                      :loading="isRegeneratingQuiz"
                      :disabled="isRegeneratingQuiz || isTyping"
                      :aria-label="t('student.lesson.quiz.regenerateAria')"
                      @click="regenerateQuiz"
                    />
                  </template>
                </v-tooltip>
              </h3>
              <QuizCard
                v-for="(q, i) in lesson.quizQuestions"
                v-show="currentQuizIndex === i || quizAnswers[q.id] !== undefined"
                :key="`${q.id}-${quizResetKey}`"
                :question="q"
                :index="i"
                @answer="onQuizAnswer"
              />
            </div>

            <v-card
              v-if="quizComplete && mistakeReview.length"
              class="glass-card review-card pa-5 mt-4"
              variant="flat"
            >
              <div class="d-flex align-center gap-2 mb-4">
                <v-icon color="warning">mdi-clipboard-alert-outline</v-icon>
                <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.quiz.reviewMistakes') }}</h3>
              </div>
              <div
                v-for="item in mistakeReview"
                :key="item.id"
                class="mistake-item pa-3 rounded-lg mb-3"
              >
                <p class="text-body-2 font-weight-medium mb-2">{{ item.question }}</p>
                <div class="text-caption mb-1">
                  <span class="text-error">{{ t('student.lesson.quiz.yourAnswer') }}</span>
                  {{ item.selected }}
                </div>
                <div class="text-caption mb-1">
                  <span class="text-success">{{ t('student.lesson.quiz.correctAnswer') }}</span>
                  {{ item.correct }}
                </div>
                <div v-if="item.hint" class="text-caption text-medium-emphasis">
                  {{ item.hint }}
                </div>
              </div>
            </v-card>

            <v-card
              v-if="quizComplete && remedialQuestions.length"
              class="glass-card remedial-card pa-5 mt-4"
              variant="flat"
            >
              <div class="d-flex align-center justify-space-between gap-3 mb-4">
                <div>
                  <span class="section-eyebrow mb-1">{{ t('student.lesson.quiz.remedial.eyebrow') }}</span>
                  <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.quiz.remedial.title') }}</h3>
                </div>
                <v-chip size="small" color="secondary" variant="tonal">
                  {{ remedialAnsweredCount }}/{{ remedialQuestions.length }}
                </v-chip>
              </div>

              <QuizCard
                v-for="(q, i) in remedialQuestions"
                :key="`${q.id}-${remedialResetKey}`"
                :question="q"
                :index="i"
                @answer="onRemedialAnswer"
              />
            </v-card>

            <v-alert
              v-if="quizComplete && !mistakeReview.length"
              type="success"
              variant="tonal"
              class="rounded-lg mt-4"
            >
              {{ t('student.lesson.quiz.noMistakes') }}
            </v-alert>
          </template>

          <v-card v-else class="glass-card pa-6 text-center" variant="flat">
            <v-progress-circular
              v-if="lesson.ai_processing"
              indeterminate
              color="secondary"
              class="mb-3"
            />
            <v-icon v-else-if="lesson.ai_error" size="48" color="error" class="mb-2">mdi-clipboard-alert</v-icon>
            <v-icon v-else size="48" color="primary" class="mb-2 opacity-70">mdi-chat-question</v-icon>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{
                lesson.ai_processing
                  ? t('student.lesson.quiz.generating')
                  : lesson.ai_error
                    ? t('student.lesson.quiz.generateFailed')
                    : hasAiSource
                      ? t('student.lesson.quiz.pendingProcessing')
                      : t('student.lesson.quiz.noAiSource')
              }}
            </p>
            <v-btn
              v-if="lesson.has_ai_chat && !lesson.has_generated_quiz && !lesson.ai_processing"
              class="mt-4"
              color="secondary"
              variant="tonal"
              prepend-icon="mdi-refresh"
              :loading="isRegeneratingQuiz"
              :disabled="isRegeneratingQuiz || isTyping"
              @click="regenerateQuiz"
            >
              {{ t('student.lesson.quiz.generateCta') }}
            </v-btn>
          </v-card>
                </div>
              </v-window-item>
            </v-window>
          </v-card>
        </div>
      </div>
    </div>

    <v-alert
      v-if="lesson.ai_processing"
      type="info"
      variant="tonal"
      class="mb-5 rounded-lg"
      prominent
    >
      <div class="d-flex align-center gap-3">
        <v-progress-circular indeterminate size="22" width="2" color="secondary" />
        <div>
          <strong>{{ t('student.lesson.ai.preparingTitle') }}</strong>
          <div class="text-caption">{{ t('student.lesson.ai.preparingHint') }}</div>
        </div>
      </div>
    </v-alert>

    <v-alert
      v-else-if="lesson.ai_error"
      type="error"
      variant="tonal"
      class="mb-5 rounded-lg"
    >
      {{ lesson.error_message || t('student.lesson.ai.processingFailed') }}
    </v-alert>

    <v-card
      v-if="!loadError && (lesson.has_video || lesson.has_pdf)"
      class="glass-card lesson-fallback-card overflow-hidden"
      variant="flat"
    >
      <span class="lesson-fallback-card__label">{{ t('student.lesson.fallback.label') }}</span>
      <v-tabs v-model="fallbackTab" color="secondary" class="lesson-fallback-tabs px-2">
        <v-tab v-if="lesson.has_video" value="video">
          <v-icon start size="18">mdi-play-circle</v-icon>
          {{ t('student.lesson.fallback.videoHint') }}
        </v-tab>
        <v-tab v-if="lesson.has_pdf" value="file">
          <v-icon start size="18">mdi-file-pdf-box</v-icon>
          {{ t('student.lesson.fallback.tabs.pdf') }}
        </v-tab>
      </v-tabs>
      <v-card-text class="pa-4 pt-2">
        <v-window v-model="fallbackTab">
          <v-window-item v-if="lesson.has_video" value="video">
            <div class="text-center pa-6 pa-md-8">
              <v-icon size="48" color="secondary" class="mb-3">mdi-play-circle-outline</v-icon>
              <p class="text-body-2 text-medium-emphasis mb-4">
                {{ t('student.lesson.fallback.videoHint') }}
              </p>
              <v-btn
                color="secondary"
                variant="tonal"
                prepend-icon="mdi-arrow-up"
                @click="scrollToLearnSection('video')"
              >
                {{ t('student.lesson.fallback.goToVideo') }}
              </v-btn>
            </div>
          </v-window-item>
          <v-window-item v-if="lesson.has_pdf" value="file">
            <div class="text-center pa-6 pa-md-8">
              <v-icon size="48" color="secondary" class="mb-3">mdi-file-pdf-box</v-icon>
              <p class="text-body-2 text-medium-emphasis mb-4">
                {{ t('student.lesson.fallback.pdfHint') }}
              </p>
              <v-btn
                color="secondary"
                variant="tonal"
                prepend-icon="mdi-arrow-up"
                @click="scrollToLearnSection('pdf')"
              >
                {{ t('student.lesson.fallback.goToPdf') }}
              </v-btn>
            </div>
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>

    <div ref="completionSectionRef">
      <LessonCompletionSection
        v-if="!loadError"
        :progress="lessonProgress"
        :loading="progressLoading"
        :verifying="verifying"
        :load-error="progressLoadError"
        @verify="onVerifyCompletion"
        @retry="loadLessonProgress"
      />
    </div>

    <v-card
      v-if="lessonProgress?.is_completed && nextLesson"
      class="glass-card pa-4 mt-4"
      variant="flat"
    >
      <v-btn
        color="success"
        variant="flat"
        prepend-icon="mdi-chevron-left"
        block
        @click="goToLesson(nextLesson.id)"
      >
        {{ t('student.lesson.nav.goToNext') }}
      </v-btn>
    </v-card>

    <v-dialog v-model="clearDialog" max-width="460">
      <v-card class="glass-card pa-5" variant="flat">
        <div class="d-flex align-center gap-3 mb-3">
          <v-avatar color="warning" variant="tonal">
            <v-icon>mdi-broom</v-icon>
          </v-avatar>
          <div>
            <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.chat.clear.title') }}</h3>
            <p class="text-caption text-medium-emphasis mb-0">{{ t('student.lesson.chat.clear.subtitle') }}</p>
          </div>
        </div>
        <p class="text-body-2 mb-5">
          {{ t('student.lesson.chat.clear.confirm') }}
        </p>
        <div class="d-flex justify-end gap-2">
          <v-btn variant="text" :disabled="isClearingChat" @click="clearDialog = false">{{ t('student.lesson.chat.clear.cancel') }}</v-btn>
          <v-btn color="warning" variant="tonal" :loading="isClearingChat" @click="confirmClearChat">
            {{ t('student.lesson.chat.clear.confirmCta') }}
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="verifyDialog" max-width="480">
      <v-card class="glass-card pa-5" variant="flat">
        <h3 class="text-h6 font-weight-bold mb-2">{{ t('student.lesson.verify.blockedTitle') }}</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">{{ verifyMessage }}</p>
        <p class="text-subtitle-2 font-weight-bold mb-2">{{ t('student.lesson.verify.requirements') }}</p>
        <v-list density="compact" class="bg-transparent mb-4">
          <v-list-item v-for="item in verifyChecklist" :key="item.key">
            <template #prepend>
              <span class="me-2">{{ item.met ? '✓' : '✗' }}</span>
            </template>
            <v-list-item-title class="text-body-2">{{ item.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
        <v-btn block rounded="lg" @click="verifyDialog = false">{{ t('student.common.ok') }}</v-btn>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import ChatPanel from '../../components/student/ChatPanel.vue'
import QuizCard from '../../components/student/QuizCard.vue'
import QuizResults from '../../components/student/QuizResults.vue'
import FeedbackCard from '../../components/student/FeedbackCard.vue'
import LessonCompletionSection from '../../components/student/LessonCompletionSection.vue'
import LessonSessionHeader from '../../components/student/lesson/LessonSessionHeader.vue'
import LessonStepStrip from '../../components/student/lesson/LessonStepStrip.vue'
import LessonLearnFlow from '../../components/student/lesson/LessonLearnFlow.vue'
import {
  clearStudentChatApi,
  fetchStudentLesson,
  generateRemedialQuestionsApi,
  regenerateQuizApi,
  submitQuizApi,
} from '../../api/student.js'
import { fetchLessonAiStatus, fetchStudentCourse, verifyLessonCompletion } from '../../api/studentCourses.js'
import { getApiBaseUrl, getErrorMessage } from '../../api/client.js'
import { useAiChat } from '../../composables/useAiChat.js'
import { useLessonProgress, buildFallbackProgress } from '../../composables/useLessonProgress.js'
import { useLessonSession } from '../../composables/useLessonSession.js'
import { useLessonLearnContinue } from '../../composables/useLessonLearnContinue.js'
import '../../assets/styles/lesson-session.css'
import '../../assets/styles/lesson-learn-flow.css'
import '../../assets/styles/lesson-embedded-teacher.css'
import { notifyLessonCompleted } from '../../utils/lessonCompletionEvents.js'
import { trackLessonViewed, trackQuizStarted } from '../../composables/useActivityTracking.js'
import { getStudentLessonById, getAvailableStudentLessons } from '../../data/studentData.js'
import { ROUTES } from '../../constants/app.js'
import { isApiMode } from '../../utils/session.js'

const props = defineProps({
  id: { type: String, required: true },
})

const route = useRoute()
const { t } = useI18n()
const router = useRouter()
const lessonId = computed(() => props.id || route.params.id)
const courseLessons = ref([])
const resolvedCourseId = ref(null)

const lesson = ref({
  title: '…',
  courseId: null,
  subject: '',
  grade: '',
  teacherName: '',
  teacherImageUrl: null,
  pdfUrl: null,
  videoUrl: null,
  has_video: false,
  has_pdf: false,
  has_ai_chat: false,
  has_generated_quiz: false,
  ai_processing: false,
  ai_error: false,
  error_message: null,
  lessonSummary: [],
  keywords: [],
  quizQuestions: [],
})

let pollTimer = null

function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = getApiBaseUrl().replace(/\/api$/, '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

const lessonVideoSrc = computed(() => mediaUrl(lesson.value.videoUrl))
const hasAiSource = computed(() => Boolean(lesson.value.has_pdf || lesson.value.has_video))

const chatDisabledHint = computed(() => {
  if (lesson.value.ai_processing) return t('student.lesson.ai.chatDisabledHint')
  return ''
})
const sessionTab = ref('chat')
const fallbackTab = ref(null)
const learnFlowRef = ref(null)
const sessionToolsRef = ref(null)

const chatStatusNotice = computed(() => {
  if (lesson.value.has_ai_chat) return ''
  if (lesson.value.ai_processing) return t('student.lesson.ai.chatDisabledHint')
  if (lesson.value.ai_error) return lesson.value.error_message || t('student.lesson.ai.assistantFailed')
  if (hasAiSource.value) return t('student.lesson.ai.waitForContent')
  return ''
})

const sessionFocusTab = computed(() => {
  if (sessionTab.value === 'chat' || sessionTab.value === 'quiz') return sessionTab.value
  if (fallbackTab.value === 'video' || fallbackTab.value === 'file') return fallbackTab.value
  return 'learn'
})

const {
  progress: lessonProgress,
  loading: progressLoading,
  loadError: progressLoadError,
  load: loadLessonProgress,
  onVideoTimeUpdate,
  onPdfProgress,
  onPdfOpened,
} = useLessonProgress(lessonId, lesson)

const completionSectionRef = ref(null)

function onVideoTimeupdate() {
  onVideoTimeUpdate(learnFlowRef.value?.getVideoElement?.() ?? null)
}

const totalLessons = computed(() => courseLessons.value.length)
const currentLessonIndex = computed(() =>
  courseLessons.value.findIndex((l) => String(l.id) === String(lessonId.value)),
)
const currentLessonNumber = computed(() =>
  currentLessonIndex.value >= 0 ? currentLessonIndex.value + 1 : 1,
)
const lessonPositionLabel = computed(() =>
  totalLessons.value ? t('student.lesson.flow.position', { n: currentLessonNumber.value, total: totalLessons.value }) : '',
)
const prevLesson = computed(() =>
  currentLessonIndex.value > 0 ? courseLessons.value[currentLessonIndex.value - 1] : null,
)
const nextLesson = computed(() =>
  currentLessonIndex.value >= 0 && currentLessonIndex.value < courseLessons.value.length - 1
    ? courseLessons.value[currentLessonIndex.value + 1]
    : null,
)
const courseBackRoute = computed(() => {
  const cid = resolvedCourseId.value || route.query.courseId
  return cid ? ROUTES.STUDENT_COURSE(cid) : ROUTES.STUDENT_COURSES
})

async function loadCourseNavigation(courseId) {
  if (!courseId) {
    courseLessons.value = []
    return
  }
  resolvedCourseId.value = Number(courseId)
  if (isApiMode()) {
    try {
      const course = await fetchStudentCourse(courseId)
      courseLessons.value = course.lessons || []
    } catch {
      courseLessons.value = []
    }
    return
  }
  courseLessons.value = getAvailableStudentLessons().map((l) => ({ id: l.id, title: l.title }))
}

function goToLesson(id) {
  if (!id || String(id) === String(lessonId.value)) return
  router.push({
    path: ROUTES.STUDENT_LESSON(id),
    query: resolvedCourseId.value ? { courseId: resolvedCourseId.value } : {},
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function onVerifyCompletion() {
  if (!isApiMode() || !lessonId.value || verifying.value) return
  verifying.value = true
  try {
    const result = await verifyLessonCompletion(lessonId.value)
    if (result.progress) {
      lessonProgress.value = result.progress
    }
    if (result.success) {
      snackbar.value = { show: true, text: result.message || t('student.lesson.verify.success'), color: 'success' }
      notifyLessonCompleted({
        lessonId: lessonId.value,
        courseId: lesson.value.courseId,
      })
    } else {
      verifyMessage.value = result.message || t('student.lesson.verify.incomplete')
      verifyChecklist.value = result.checklist || []
      verifyDialog.value = true
    }
  } catch (err) {
    snackbar.value = {
      show: true,
      text: getErrorMessage(err, t('student.lesson.errors.verify')),
      color: 'error',
    }
  } finally {
    verifying.value = false
  }
}

function pickDefaultTab() {
  scrollToLearnFlow()
}

function scrollToLearnSection(key) {
  learnFlowRef.value?.scrollToSection(key)
}

function scrollToLearnFlow() {
  scrollToLearnSection('start')
}

function runLearnContinue(action) {
  switch (action) {
    case 'scrollVideo':
      scrollToLearnSection('video')
      break
    case 'scrollPdf':
      scrollToLearnSection('pdf')
      break
    case 'scrollStart':
      scrollToLearnSection('start')
      break
    case 'goChat':
      openChatExperience()
      break
    case 'goQuiz':
      openQuizExperience()
      break
    default:
      break
  }
}

const chatPanelRef = ref(null)
const activeFeedback = ref([])
const quizAnswers = reactive({})
const remedialAnswers = reactive({})
const remedialQuestions = ref([])
const quizResetKey = ref(0)
const remedialResetKey = ref(0)
const loadError = ref('')
const clearDialog = ref(false)
const isClearingChat = ref(false)
const isRegeneratingQuiz = ref(false)
const isGeneratingRemedial = ref(false)
const submittedQuiz = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })
const verifying = ref(false)
const verifyDialog = ref(false)
const verifyMessage = ref('')
const verifyChecklist = ref([])

const {
  messages,
  chatInput,
  isTyping,
  voiceTtsAvailable,
  voiceTtsMessage,
  sendMessage,
  sendVoiceMessage,
  loadConversation,
  setLessonId,
  applyVoiceTtsStatus,
} = useAiChat([], [])

const answeredCount = computed(() => Object.keys(quizAnswers).length)
const quizTotal = computed(() => lesson.value.quizQuestions?.length ?? 0)
const quizComplete = computed(() => {
  const total = quizTotal.value
  return total > 0 && answeredCount.value >= total
})

const studentQuestionCount = computed(() =>
  messages.value.filter((message) => message.role === 'student').length,
)

const quizScore = computed(() => {
  let correct = 0
  for (const q of lesson.value.quizQuestions || []) {
    if (quizAnswers[q.id] === q.correctIndex) correct += 1
  }
  return { correct }
})

const mistakeReview = computed(() =>
  (lesson.value.quizQuestions || [])
    .filter((q) => quizAnswers[q.id] !== undefined && quizAnswers[q.id] !== q.correctIndex)
    .map((q) => ({
      id: q.id,
      question: q.question,
      selected: q.options[quizAnswers[q.id]] ?? t('student.lesson.quiz.noAnswer'),
      correct: q.options[q.correctIndex],
      hint: q.hint,
    })),
)

const remedialAnsweredCount = computed(() => Object.keys(remedialAnswers).length)

const progressPercent = computed(() => {
  const askedTutor = studentQuestionCount.value > 0 ? 1 : 0
  const quizCompletion = quizTotal.value ? answeredCount.value / quizTotal.value : 0
  const quizMastery = quizComplete.value && quizTotal.value ? quizScore.value.correct / quizTotal.value : 0
  const summaryProgress = lesson.value.lessonSummary?.length ? 1 : 0
  return Math.min(
    100,
    Math.round(summaryProgress * 10 + askedTutor * 15 + quizCompletion * 25 + quizMastery * 50),
  )
})

const progressNextStep = computed(() => {
  if (!quizTotal.value) {
    return {
      icon: 'mdi-clipboard-plus-outline',
      text: t('student.lesson.flow.generateQuiz.text'),
      action: 'regenerateQuiz',
      cta: t('student.lesson.flow.generateQuiz.cta'),
    }
  }
  if (!quizComplete.value) {
    const remaining = Math.max(quizTotal.value - answeredCount.value, 0)
    return {
      icon: 'mdi-clipboard-text-clock-outline',
      text: remainingQuizText(remaining),
      action: null,
      cta: '',
    }
  }
  if (mistakeReview.value.length) {
    const mistakes = mistakeReview.value.length
    return {
      icon: 'mdi-clipboard-alert-outline',
      text:
        mistakes === 1 ? t('student.lesson.flow.mistakes.one')
          : t('student.lesson.flow.mistakes.many', { n: mistakes }),
      action: 'regenerateQuiz',
      cta: t('student.lesson.flow.mistakes.cta'),
    }
  }
  if (studentQuestionCount.value < 1) {
    return {
      icon: 'mdi-message-question-outline',
      text: t('student.lesson.flow.askTeacher.text'),
      action: 'askKeywords',
      cta: t('student.lesson.flow.askTeacher.cta'),
    }
  }
  return {
    icon: 'mdi-check-decagram-outline',
    text: t('student.lesson.flow.complete.text'),
    action: 'regenerateQuiz',
    cta: t('student.lesson.flow.complete.cta'),
  }
})

const progressActionDisabled = computed(() => {
  if (progressNextStep.value.action === 'askKeywords') return isTyping.value
  if (progressNextStep.value.action === 'regenerateQuiz') return isRegeneratingQuiz.value || isTyping.value
  return true
})

const {
  sessionSteps,
  sessionProgressPercent,
  headerNextAction,
  learnComplete,
} = useLessonSession({
  lesson,
  lessonProgress,
  activeTab: sessionFocusTab,
  studentQuestionCount,
  quizComplete,
  mistakeReview,
  progressNextStep,
  progressPercent,
  progressActionDisabled,
  verifying,
  nextLesson,
})

const learnContinueAction = useLessonLearnContinue({
  lesson,
  lessonProgress,
  learnComplete,
  studentQuestionCount,
})

const learningPlanLabel = computed(() =>
  mistakeReview.value.length ? t('student.lesson.flow.plan.reviewLabel') : t('student.lesson.flow.plan.consolidateLabel'),
)

const learningPlanItems = computed(() => {
  if (!quizComplete.value) return []

  const firstMistake = mistakeReview.value[0]
  if (mistakeReview.value.length) {
    return [
      {
        id: 'review',
        icon: 'mdi-book-open-page-variant',
        color: 'warning',
        title: t('student.lesson.flow.plan.reviewMistake.title'),
        description: firstMistake
          ? t('student.lesson.flow.plan.reviewMistake.withAnswer', { answer: firstMistake.correct })
          : t('student.lesson.flow.plan.reviewMistake.generic'),
      },
      {
        id: 'ask',
        icon: 'mdi-message-question',
        color: 'primary',
        title: t('student.lesson.flow.plan.askTeacher.title'),
        description: t('student.lesson.flow.plan.askTeacher.description'),
        action: 'askMistake',
        cta: t('student.lesson.flow.plan.askTeacher.cta'),
      },
      {
        id: 'remedial',
        icon: 'mdi-target',
        color: 'secondary',
        title: t('student.lesson.flow.plan.remedial.title'),
        description: t('student.lesson.flow.plan.remedial.description'),
        action: 'generateRemedial',
        cta: remedialQuestions.value.length ? t('student.lesson.flow.plan.remedial.regenerate') : t('student.lesson.flow.plan.remedial.start'),
      },
      {
        id: 'retry',
        icon: 'mdi-refresh',
        color: 'warning',
        title: t('student.lesson.flow.plan.followUp.title'),
        description: t('student.lesson.flow.plan.followUp.description'),
        action: 'regenerateQuiz',
        cta: t('student.lesson.flow.mistakes.cta'),
      },
    ]
  }

  const keywordText = lesson.value.keywords?.slice(0, 3).join('، ')
  return [
    {
      id: 'done',
      icon: 'mdi-check-decagram-outline',
      color: 'success',
      title: t('student.lesson.flow.plan.mastery.title'),
      description: t('student.lesson.flow.plan.mastery.description'),
    },
    {
      id: 'challenge',
      icon: 'mdi-brain',
      color: 'primary',
      title: t('student.lesson.flow.plan.challenge.title'),
      description: keywordText ? t('student.lesson.flow.plan.challenge.withKeywords', { keywords: keywordText }) : t('student.lesson.flow.plan.challenge.generic'),
      action: 'askChallenge',
      cta: t('student.lesson.flow.plan.challenge.cta'),
    },
    {
      id: 'new-quiz',
      icon: 'mdi-clipboard-plus-outline',
      color: 'secondary',
      title: t('student.lesson.flow.plan.newQuiz.title'),
      description: t('student.lesson.flow.plan.newQuiz.description'),
      action: 'regenerateQuiz',
      cta: t('student.lesson.flow.mistakes.cta'),
    },
  ]
})

const currentQuizIndex = computed(() => {
  const qs = lesson.value.quizQuestions || []
  const next = qs.findIndex((q) => quizAnswers[q.id] === undefined)
  return next >= 0 ? next : qs.length - 1
})

function remainingQuizText(remaining) {
  if (remaining <= 0) return t('student.lesson.flow.quiz.remaining.done')
  if (remaining === 1) return t('student.lesson.flow.quiz.remaining.one')
  if (remaining === 2) return t('student.lesson.flow.quiz.remaining.two')
  return t('student.lesson.flow.quiz.remaining.many', { n: remaining })
}

async function loadLesson() {
  loadError.value = ''
  activeFeedback.value = []
  Object.keys(quizAnswers).forEach((k) => delete quizAnswers[k])
  clearRemedialPractice()
  quizResetKey.value += 1
  submittedQuiz.value = false
  stopPolling()

  if (isApiMode()) {
    try {
      const data = await fetchStudentLesson(lessonId.value)
      lesson.value = {
        ...data,
        courseId: data.courseId ?? data.course_id ?? route.query.courseId ?? null,
        teacherImageUrl: data.teacherImageUrl ?? data.teacher_image_url ?? null,
      }
      await loadCourseNavigation(lesson.value.courseId)
      applyVoiceTtsStatus(data)
      loadConversation(data.chatMessages || [], [])
      setLessonId(Number(lessonId.value))
      trackLessonViewed(lessonId.value)
      await loadLessonProgress()
      if (data.ai_processing) startPolling()
      pickDefaultTab()
    } catch (err) {
      lesson.value = {
        title: t('student.lesson.errors.loadTitle'),
        subject: '',
        grade: '',
        teacherName: '',
        pdfUrl: null,
        videoUrl: null,
        has_video: false,
        has_pdf: false,
        has_ai_chat: false,
        has_generated_quiz: false,
        ai_processing: false,
        ai_error: false,
        error_message: null,
        lessonSummary: [],
        keywords: [],
        quizQuestions: [],
      }
      loadConversation([], [])
      setLessonId(null)
      loadError.value = getErrorMessage(err, t('student.lesson.errors.load'))
      return
    }
  } else {
    const l = getStudentLessonById(lessonId.value)
    lesson.value = { ...l, courseId: route.query.courseId || 1 }
    await loadCourseNavigation(lesson.value.courseId)
    loadConversation(l.chatMessages, l.aiResponses)
    lessonProgress.value = buildFallbackProgress(lessonId.value, lesson.value)
  }
  chatPanelRef.value?.scrollToBottom()
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    try {
      const status = await fetchLessonAiStatus(lessonId.value)
      if (!status.ai_processing) {
        stopPolling()
        await loadLesson()
        pickDefaultTab()
      } else {
        lesson.value = { ...lesson.value, ...status }
      }
    } catch {
      /* ignore transient poll errors */
    }
  }, 4000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onUnmounted(stopPolling)

watch(lessonId, loadLesson, { immediate: true })

watch(fallbackTab, (tab) => {
  if (tab === 'video') scrollToLearnSection('video')
  if (tab === 'file') scrollToLearnSection('pdf')
})

watch(messages, () => {
  chatPanelRef.value?.scrollToBottom()
}, { deep: true })

function onSend() {
  sendMessage()
}

function onVoice(blob) {
  sendVoiceMessage(blob)
}

function askTutor(prompt) {
  askTeacherPrompt(prompt)
}

async function askTeacherPrompt(prompt, { autoSend = true, focus = true } = {}) {
  if (isTyping.value) return
  await openChatExperience({ focus: focus && !autoSend })
  chatInput.value = prompt
  if (autoSend && lesson.value.has_ai_chat) {
    sendMessage()
  }
}

const CONCEPT_ACTION_PROMPTS = {
  explain: (concept) => t('student.lesson.concepts.explainPrompt', { concept }),
  example: (concept) => t('student.lesson.concepts.examplePrompt', { concept }),
  quiz: (concept) => t('student.lesson.concepts.quizPrompt', { concept }),
}

function onConceptAction({ concept, action }) {
  if (!concept || isTyping.value) return
  if (action === 'ask') {
    askTeacherPrompt(t('student.lesson.concepts.askPrompt', { concept }), { autoSend: false, focus: true })
    return
  }
  const buildPrompt = CONCEPT_ACTION_PROMPTS[action] || CONCEPT_ACTION_PROMPTS.explain
  askTeacherPrompt(buildPrompt(concept))
}

function runProgressAction() {
  if (progressActionDisabled.value) return
  if (progressNextStep.value.action === 'regenerateQuiz') {
    regenerateQuiz()
    return
  }
  if (progressNextStep.value.action === 'askKeywords') {
    const keywordText = lesson.value.keywords?.slice(0, 4).join('، ')
    askTutor(keywordText ? t('student.lesson.flow.plan.challenge.withKeywords', { keywords: keywordText }) : t('student.lesson.flow.plan.challenge.generic'))
  }
}

function scrollToCompletion() {
  completionSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function openQuizExperience() {
  sessionTab.value = 'quiz'
  if (lessonId.value) trackQuizStarted(lessonId.value)
  nextTick(() => {
    const toolsEl = sessionToolsRef.value?.$el ?? sessionToolsRef.value
    toolsEl?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

async function openChatExperience({ focus = true } = {}) {
  sessionTab.value = 'chat'
  await nextTick()
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))

  const toolsEl = sessionToolsRef.value?.$el ?? sessionToolsRef.value
  toolsEl?.scrollIntoView({ behavior: 'smooth', block: 'start' })

  await nextTick()
  chatPanelRef.value?.scrollToBottom?.()

  if (focus && lesson.value.has_ai_chat && !lesson.value.sendDisabled) {
    await new Promise((resolve) => setTimeout(resolve, 120))
    chatPanelRef.value?.focusInput?.()
  }
}

function onStepSelect(stepId) {
  if (stepId === 'learn') {
    scrollToLearnFlow()
    return
  }
  if (stepId === 'ask') {
    openChatExperience()
    return
  }
  if (stepId === 'quiz') {
    openQuizExperience()
    return
  }
  if (stepId === 'complete') {
    scrollToCompletion()
  }
}

function runHeaderAction(action) {
  switch (action) {
    case 'scrollVideo':
      scrollToLearnSection('video')
      break
    case 'scrollPdf':
      scrollToLearnSection('pdf')
      break
    case 'scrollStart':
      scrollToLearnFlow()
      break
    case 'goChat':
      openChatExperience()
      break
    case 'goQuiz':
      openQuizExperience()
      break
    case 'verify':
      scrollToCompletion()
      break
    case 'nextLesson':
      if (nextLesson.value) goToLesson(nextLesson.value.id)
      break
    case 'backToCourse':
      router.push(courseBackRoute.value)
      break
    case 'regenerateQuiz':
      regenerateQuiz()
      break
    case 'askKeywords':
      runProgressAction()
      break
    default:
      break
  }
}

function learningPlanActionDisabled(action) {
  if (action === 'regenerateQuiz') return isRegeneratingQuiz.value || isTyping.value
  if (action === 'generateRemedial') return isGeneratingRemedial.value || isTyping.value
  return isTyping.value
}

function learningPlanActionLoading(action) {
  if (action === 'regenerateQuiz') return isRegeneratingQuiz.value
  if (action === 'generateRemedial') return isGeneratingRemedial.value
  return false
}

function runLearningPlanAction(action) {
  if (learningPlanActionDisabled(action)) return
  if (action === 'regenerateQuiz') {
    regenerateQuiz()
    return
  }
  if (action === 'generateRemedial') {
    generateRemedialPractice()
    return
  }
  if (action === 'askMistake') {
    const mistake = mistakeReview.value[0]
    if (!mistake) return
    askTutor(
      t('student.lesson.flow.prompts.explainMistake', {
        question: mistake.question,
        selected: mistake.selected,
        correct: mistake.correct,
      }),
    )
    return
  }
  if (action === 'askChallenge') {
    const keywordText = lesson.value.keywords?.slice(0, 4).join('، ')
    askTutor(keywordText ? t('student.lesson.flow.prompts.shortChallengeWithKeywords', { keywords: keywordText }) : t('student.lesson.flow.prompts.shortChallengeGeneric'))
  }
}

async function generateRemedialPractice() {
  if (isGeneratingRemedial.value || !lessonId.value || !mistakeReview.value.length) return
  isGeneratingRemedial.value = true
  try {
    if (isApiMode()) {
      remedialQuestions.value = await generateRemedialQuestionsApi({
        lessonId: Number(lessonId.value),
        answers: { ...quizAnswers },
      })
    } else {
      remedialQuestions.value = mistakeReview.value.slice(0, 2).map((item, index) => ({
        id: `remedial-${index}`,
        question: t('student.lesson.flow.prompts.remedialQuestion', { question: item.question }),
        options: lesson.value.quizQuestions[index]?.options || [item.correct, item.selected, t('student.lesson.flow.prompts.optionOther'), t('student.lesson.flow.prompts.optionNone')],
        correctIndex: 0,
        hint: item.hint,
      }))
    }
    Object.keys(remedialAnswers).forEach((k) => delete remedialAnswers[k])
    remedialResetKey.value += 1
    snackbar.value = { show: true, text: t('student.lesson.snackbar.remedialGenerated'), color: 'success' }
  } catch (err) {
    snackbar.value = {
      show: true,
      text: getErrorMessage(err, t('student.lesson.snackbar.remedialGenerateFailed')),
      color: 'error',
    }
  } finally {
    isGeneratingRemedial.value = false
  }
}

function openClearDialog() {
  if (!messages.value.length || isTyping.value) return
  clearDialog.value = true
}

async function confirmClearChat() {
  if (isClearingChat.value) return
  isClearingChat.value = true
  try {
    if (isApiMode() && lessonId.value) {
      await clearStudentChatApi(lessonId.value)
      const data = await fetchStudentLesson(lessonId.value)
      lesson.value = {
        ...data,
        teacherImageUrl: data.teacherImageUrl ?? data.teacher_image_url ?? null,
      }
      applyVoiceTtsStatus(data)
      loadConversation(data.chatMessages || [], [])
    } else {
      loadConversation([], [])
    }
    clearDialog.value = false
    snackbar.value = { show: true, text: t('student.lesson.snackbar.chatCleared'), color: 'success' }
    chatPanelRef.value?.scrollToBottom()
  } catch (err) {
    snackbar.value = {
      show: true,
      text: getErrorMessage(err, t('student.lesson.snackbar.chatClearFailed')),
      color: 'error',
    }
  } finally {
    isClearingChat.value = false
  }
}

function onQuizAnswer({ correct, questionId, selectedIndex }) {
  quizAnswers[questionId] = selectedIndex
  clearRemedialPractice()
  activeFeedback.value = [
    correct
      ? {
          id: Date.now(),
          type: 'success',
          title: t('student.lesson.feedback.quizCorrectTitle'),
          message: t('student.lesson.feedback.quizCorrectMessage'),
        }
      : {
          id: Date.now(),
          type: 'hint',
          title: t('student.lesson.feedback.quizWrongTitle'),
          message: t('student.lesson.feedback.quizWrongMessage'),
        },
  ]
  submitCompletedQuizIfNeeded()
}

function onRemedialAnswer({ correct, questionId, selectedIndex }) {
  remedialAnswers[questionId] = selectedIndex
  activeFeedback.value = [
    correct
      ? {
          id: Date.now(),
          type: 'success',
          title: t('student.lesson.feedback.remedialCorrectTitle'),
          message: t('student.lesson.feedback.remedialCorrectMessage'),
        }
      : {
          id: Date.now(),
          type: 'hint',
          title: t('student.lesson.feedback.remedialWrongTitle'),
          message: t('student.lesson.feedback.remedialWrongMessage'),
        },
  ]
}

function clearRemedialPractice() {
  remedialQuestions.value = []
  Object.keys(remedialAnswers).forEach((k) => delete remedialAnswers[k])
  remedialResetKey.value += 1
}

function resetQuiz() {
  Object.keys(quizAnswers).forEach((k) => delete quizAnswers[k])
  activeFeedback.value = []
  clearRemedialPractice()
  quizResetKey.value += 1
  submittedQuiz.value = false
}

async function submitCompletedQuizIfNeeded() {
  if (!isApiMode() || submittedQuiz.value || !quizComplete.value || !lessonId.value) return
  submittedQuiz.value = true
  try {
    await submitQuizApi({
      lessonId: Number(lessonId.value),
      answers: { ...quizAnswers },
    })
    await loadLessonProgress()
    if (lessonProgress.value?.is_completed) {
      snackbar.value = {
        show: true,
        text: t('student.lesson.snackbar.quizSubmittedFinish'),
        color: 'info',
      }
    }
  } catch (err) {
    snackbar.value = {
      show: true,
      text: getErrorMessage(err, t('student.lesson.snackbar.quizSubmitFailed')),
      color: 'warning',
    }
  }
}

async function regenerateQuiz() {
  if (isRegeneratingQuiz.value || !lessonId.value) return
  isRegeneratingQuiz.value = true
  try {
    if (isApiMode()) {
      const quizQuestions = await regenerateQuizApi(lessonId.value)
      lesson.value = {
        ...lesson.value,
        quizQuestions,
      }
    }
    resetQuiz()
    snackbar.value = { show: true, text: t('student.lesson.snackbar.quizRegenerated'), color: 'success' }
  } catch (err) {
    snackbar.value = {
      show: true,
      text: getErrorMessage(err, t('student.lesson.snackbar.quizRegenerateFailed')),
      color: 'error',
    }
  } finally {
    isRegeneratingQuiz.value = false
  }
}
</script>

<style scoped>
.lesson-course-nav {
  position: sticky;
  top: 72px;
  z-index: 6;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.lesson-course-nav__row {
  width: 100%;
}

.lesson-course-nav__back {
  flex-shrink: 0;
}

.lesson-course-nav__arrows {
  flex-shrink: 0;
}

@media (max-width: 600px) {
  .lesson-course-nav {
    top: 64px;
  }

  .lesson-course-nav__row {
    flex-direction: column;
    align-items: stretch;
  }

  .lesson-course-nav__arrows {
    width: 100%;
  }

  .lesson-course-nav__arrows .v-btn {
    flex: 1;
  }
}

.lesson-tabs {
  background: rgba(0, 0, 0, 0.15);
}

.tab-panel {
  min-height: 360px;
}

.lesson-window {
  overflow: visible;
}

.lesson-sidebar {
  position: relative;
  top: 0;
}

@media (max-width: 1279px) {
  .lesson-sidebar {
    position: static;
  }
}

.min-width-0 {
  min-width: 0;
}

.learning-progress,
.learning-plan,
.remedial-card,
.review-card {
  border: 1px solid var(--em-border);
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.next-step {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 62px;
  padding: 10px;
  border: 1px solid rgba(34, 211, 238, 0.2);
  border-radius: 8px;
  background: rgba(34, 211, 238, 0.07);
}

.next-step__copy {
  min-width: 0;
  flex: 1;
}

.next-step__copy span {
  display: block;
  color: var(--em-cyan);
  font-size: 0.72rem;
  margin-bottom: 2px;
}

.next-step__copy strong {
  display: block;
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.84rem;
  line-height: 1.45;
}

.progress-stat {
  min-height: 74px;
  border: 1px solid rgba(124, 108, 240, 0.18);
  border-radius: 8px;
  background: rgba(8, 12, 24, 0.34);
  display: grid;
  place-items: center;
  align-content: center;
  gap: 3px;
  text-align: center;
}

.progress-stat strong {
  font-size: 1rem;
  line-height: 1.1;
}

.progress-stat span {
  color: var(--em-text-muted);
  font-size: 0.74rem;
}

.mistake-item {
  border: 1px solid rgba(248, 113, 113, 0.22);
  background: rgba(248, 113, 113, 0.07);
}

.learning-plan {
  overflow: hidden;
}

.learning-plan__list {
  display: grid;
  gap: 10px;
}

.learning-plan__item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 70px;
  padding: 10px;
  border: 1px solid rgba(124, 108, 240, 0.18);
  border-radius: 8px;
  background: rgba(8, 12, 24, 0.32);
}

.learning-plan__icon {
  flex: 0 0 auto;
}

.learning-plan__copy {
  min-width: 0;
  flex: 1;
}

.learning-plan__copy strong {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  line-height: 1.4;
}

.learning-plan__copy span {
  display: block;
  margin-top: 2px;
  color: var(--em-text-muted);
  font-size: 0.78rem;
  line-height: 1.55;
}

@media (max-width: 600px) {
  .learning-plan__item {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .learning-plan__item :deep(.v-btn) {
    margin-inline-start: 46px;
  }
}

.feedback-enter-active {
  transition: all 0.35s ease;
}

.feedback-enter-from {
  opacity: 0;
  transform: translateX(12px);
}
</style>
