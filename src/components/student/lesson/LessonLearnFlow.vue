<template>
  <v-card
    ref="rootRef"
    class="glass-card lesson-learn-flow overflow-hidden"
    variant="flat"
    :aria-label="t('student.lesson.learn.ariaLabel')"
  >
    <div class="lesson-learn-flow__inner pa-4 pa-md-5">
      <header class="lesson-learn-flow__intro mb-5">
        <div class="d-flex align-center gap-3 mb-3">
          <TeacherAvatar
            :name="teacherName"
            :image-url="teacherImageUrl"
            :size="52"
            class="lesson-learn-flow__avatar"
          />
          <div class="min-width-0">
            <span class="section-eyebrow mb-1">{{ t('student.lesson.learn.eyebrow') }}</span>
            <h2 class="text-h6 text-md-h5 font-weight-bold mb-0">
              {{ t('student.lesson.learn.titleWithTeacher', { teacher: teacherName }) }}
            </h2>
          </div>
        </div>
        <p class="lesson-learn-flow__guide text-body-2 text-medium-emphasis mb-0">
          {{ learnGuideText }}
        </p>
      </header>

      <div class="lesson-learn-flow__stream">
        <section
          v-if="hasVideo"
          id="learn-video"
          class="lesson-learn-flow__section lesson-learn-flow__section--video"
        >
          <div class="lesson-learn-flow__section-head mb-3">
            <v-icon color="secondary" size="22" class="me-2">mdi-play-circle</v-icon>
            <div>
              <span class="section-eyebrow mb-0">{{ t('student.lesson.learn.stepLabel', { n: 1 }) }}</span>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">
                {{ t('student.lesson.learn.startWatching', { teacher: teacherName }) }}
              </h3>
            </div>
          </div>
          <div v-if="videoSrc" class="lesson-learn-flow__video-wrap" :class="{ 'lesson-learn-flow__video-wrap--embed': embedInfo }">
            <iframe
              v-if="embedInfo"
              class="lesson-learn-flow__embed"
              :src="embedInfo.embedUrl"
              :title="t('student.lesson.learn.videoTitle')"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
            />
            <video
              v-else
              ref="videoEl"
              class="lesson-learn-flow__video"
              controls
              playsinline
              :src="videoSrc"
              @timeupdate="$emit('video-timeupdate')"
            />
          </div>
          <v-card v-else class="glass-card pa-8 text-center" variant="flat">
            <v-icon size="48" color="grey" class="mb-2">mdi-video-off-outline</v-icon>
            <p class="text-body-2 text-medium-emphasis mb-0">{{ t('student.lesson.learn.videoUnavailable') }}</p>
          </v-card>
        </section>

        <div
          v-if="hasVideo && (hasPdf || hasSummary || hasKeywords)"
          class="lesson-learn-flow__divider"
          aria-hidden="true"
        >
          ↓
        </div>

        <section
          v-if="hasPdf"
          id="learn-pdf"
          class="lesson-learn-flow__section lesson-learn-flow__section--pdf"
        >
          <div class="lesson-learn-flow__section-head mb-3">
            <v-icon color="secondary" size="22" class="me-2">mdi-file-pdf-box</v-icon>
            <div>
              <span class="section-eyebrow mb-0">{{ t('student.lesson.learn.stepLabel', { n: hasVideo ? 2 : 1 }) }}</span>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">
                {{ hasVideo ? t('student.lesson.learn.continueReading') : t('student.lesson.learn.pdfHeadline', { teacher: teacherName }) }}
              </h3>
            </div>
          </div>
          <LessonPdfViewer
            :url="pdfUrl"
            @opened="$emit('pdf-opened')"
            @progress="$emit('pdf-progress', $event)"
          />
          <p v-if="preview" class="text-body-2 text-medium-emphasis mt-4 mb-0">{{ preview }}</p>
        </section>

        <div
          v-if="hasPdf && (hasSummary || hasKeywords)"
          class="lesson-learn-flow__divider"
          aria-hidden="true"
        >
          ↓
        </div>

        <section
          v-if="hasSummary"
          id="learn-summary"
          class="lesson-learn-flow__section lesson-learn-flow__section--summary"
        >
          <div class="lesson-learn-flow__section-head mb-3">
            <v-icon color="secondary" size="22" class="me-2">mdi-help-circle-outline</v-icon>
            <div>
              <span class="section-eyebrow mb-0">{{ t('student.lesson.learn.reviewWithTeacher') }}</span>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('student.lesson.learn.understoodIdeas') }}</h3>
            </div>
          </div>
          <LessonRecapIdeas :ideas="summary" />
        </section>

        <div
          v-if="hasSummary && hasKeywords"
          class="lesson-learn-flow__divider"
          aria-hidden="true"
        >
          ↓
        </div>

        <section
          v-if="hasKeywords"
          id="learn-keywords"
          class="lesson-learn-flow__section lesson-learn-flow__section--keywords lesson-learn-flow__section--recap-keywords"
        >
          <div class="lesson-learn-flow__section-head mb-3">
            <v-icon color="secondary" size="22" class="me-2">mdi-star-circle</v-icon>
            <div>
              <span class="section-eyebrow mb-0">{{ t('student.lesson.learn.consolidateConcepts') }}</span>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('student.lesson.learn.coreConcepts') }}</h3>
            </div>
          </div>
          <LessonConceptRecap
            :concepts="keywords"
            :teacher-name="teacherName"
            :teacher-image-url="teacherImageUrl"
            :disabled="!hasAiChat || chatDisabled"
            @concept-action="(payload) => $emit('concept-action', payload)"
          />
        </section>

        <div
          v-if="showTeacherHelper && hasContentBeforeHelper"
          class="lesson-learn-flow__divider"
          aria-hidden="true"
        >
          ↓
        </div>

        <section
          v-if="showTeacherHelper"
          id="learn-teacher-helper"
          class="lesson-learn-flow__section lesson-learn-flow__section--teacher"
        >
          <TeacherHelperCard
            :teacher-name="teacherName"
            :teacher-image-url="teacherImageUrl"
            :disabled="!hasAiChat || chatDisabled"
            :hint="teacherHelperHint"
            @ask="$emit('ask-teacher')"
          />
        </section>

        <div
          v-if="showTeacherHelper"
          class="lesson-learn-flow__divider"
          aria-hidden="true"
        >
          ↓
        </div>

        <section
          id="learn-continue"
          class="lesson-learn-flow__section lesson-learn-flow__section--continue mt-2"
        >
          <div class="lesson-learn-flow__continue pa-4 pa-md-5">
            <div class="d-flex align-start gap-3 flex-wrap">
              <v-icon :icon="continueAction.icon" color="secondary" size="28" class="flex-shrink-0 mt-1" />
              <div class="flex-grow-1 min-width-0">
                <span class="section-eyebrow mb-1">{{ continueAction.eyebrow }}</span>
                <p class="text-body-1 font-weight-medium mb-0">{{ continueAction.message }}</p>
              </div>
              <v-btn
                color="secondary"
                variant="flat"
                size="large"
                class="lesson-learn-flow__continue-btn flex-shrink-0"
                :prepend-icon="continueAction.icon"
                @click="$emit('continue', continueAction.action)"
              >
                {{ continueAction.cta }}
              </v-btn>
            </div>
          </div>
        </section>
      </div>

      <v-card
        v-if="!hasVideo && !hasPdf && !hasSummary && !hasKeywords"
        class="glass-card pa-10 text-center mt-4"
        variant="flat"
      >
        <v-icon size="56" color="grey" class="mb-3">mdi-book-open-page-variant</v-icon>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ t('student.lesson.learn.emptyContent') }}
        </p>
        <TeacherHelperCard
          v-if="showTeacherHelper"
          class="mb-4"
          :teacher-name="teacherName"
          :teacher-image-url="teacherImageUrl"
          :disabled="!hasAiChat || chatDisabled"
          :hint="teacherHelperHint"
          @ask="$emit('ask-teacher')"
        />
        <v-btn
          color="secondary"
          variant="flat"
          :prepend-icon="continueAction.icon"
          @click="$emit('continue', continueAction.action)"
        >
          {{ continueAction.cta }}
        </v-btn>
      </v-card>
    </div>
  </v-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'
import TeacherHelperCard from './TeacherHelperCard.vue'
import LessonRecapIdeas from './LessonRecapIdeas.vue'
import LessonConceptRecap from './LessonConceptRecap.vue'
import LessonPdfViewer from '../LessonPdfViewer.vue'
import { resolveVideoEmbed } from '../../../utils/videoEmbed.js'
import '../../../assets/styles/lesson-recap.css'

const { t } = useI18n()

const props = defineProps({
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  videoSrc: { type: String, default: '' },
  pdfUrl: { type: String, default: '' },
  preview: { type: String, default: '' },
  summary: { type: Array, default: () => [] },
  keywords: { type: Array, default: () => [] },
  hasVideo: { type: Boolean, default: false },
  hasPdf: { type: Boolean, default: false },
  hasAiChat: { type: Boolean, default: false },
  chatDisabled: { type: Boolean, default: false },
  chatDisabledHint: { type: String, default: '' },
  continueAction: {
    type: Object,
    default: () => ({
      eyebrow: '',
      message: '',
      cta: '',
      action: '',
      icon: 'mdi-arrow-left',
    }),
  },
})

defineEmits([
  'video-timeupdate',
  'pdf-opened',
  'pdf-progress',
  'continue',
  'ask-teacher',
  'concept-action',
])

const rootRef = ref(null)
const videoEl = ref(null)

const embedInfo = computed(() => resolveVideoEmbed(props.videoSrc))

const hasSummary = computed(() => props.summary?.length > 0)
const hasKeywords = computed(() => props.keywords?.length > 0)
const showTeacherHelper = computed(() => props.hasAiChat)
const hasContentBeforeHelper = computed(
  () => props.hasVideo || props.hasPdf || hasSummary.value || hasKeywords.value,
)
const teacherHelperHint = computed(() => {
  if (props.chatDisabledHint) return props.chatDisabledHint
  if (!props.hasAiChat) return ''
  if (props.chatDisabled) return t('student.lesson.learn.chatDisabled')
  return ''
})

const learnGuideText = computed(() => {
  const parts = []
  if (props.hasVideo) parts.push(t('student.lesson.learn.prompts.watch'))
  if (props.hasPdf) parts.push(t('student.lesson.learn.prompts.read'))
  if (hasSummary.value) parts.push(t('student.lesson.learn.prompts.review'))
  if (hasKeywords.value) parts.push(t('student.lesson.learn.prompts.interact'))
  if (!parts.length) return t('student.lesson.learn.prompts.empty')
  return t('student.lesson.learn.prompts.joined', { parts: parts.join('، ') })
})

const SECTION_IDS = {
  start: 'learn-video',
  video: 'learn-video',
  pdf: 'learn-pdf',
  summary: 'learn-summary',
  keywords: 'learn-keywords',
  teacher: 'learn-teacher-helper',
  continue: 'learn-continue',
}

function scrollToSection(key) {
  const resolved = key === 'start'
    ? (props.hasVideo ? 'video' : props.hasPdf ? 'pdf' : 'continue')
    : key
  const id = SECTION_IDS[resolved] || `learn-${resolved}`
  const el = typeof document !== 'undefined' ? document.getElementById(id) : null
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    return
  }
  rootRef.value?.$el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

defineExpose({
  scrollToSection,
  getVideoElement: () => videoEl.value,
})
</script>
