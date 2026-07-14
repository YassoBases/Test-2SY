<template>
  <LessonWorkspaceScreen
    :open="modelValue"
    workspace-class="add-lesson-workspace"
    eyebrow=""
    title=""
    :busy="saving"
    @close="close"
  >
    <div class="add-lesson-workspace__body">
      <header class="add-lesson-workspace__hero">
        <p class="add-lesson-workspace__eyebrow">{{ $t('teacher.lessons.createEyebrow') }}</p>
        <h2 class="add-lesson-workspace__hero-title">{{ $t('teacher.lessons.newLesson') }}</h2>
        <p class="add-lesson-workspace__hero-intro">
          {{ $t('teacher.lessons.newLessonSubtitle') }}
        </p>
      </header>

      <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">{{ error }}</v-alert>

      <section class="add-lesson-section" aria-labelledby="add-lesson-info-title">
        <div class="add-lesson-section__head">
          <h3 id="add-lesson-info-title" class="add-lesson-section__title">{{ $t('teacher.lessons.infoSection') }}</h3>
        </div>

        <div class="add-lesson-field-stack">
          <div class="add-lesson-field-block">
            <div class="add-lesson-field-header">
              <span class="add-lesson-field-label">{{ $t('teacher.lessons.lessonTitleAsterisk') }}</span>
              <button
                type="button"
                class="add-lesson-field-generate"
                :disabled="!!generating"
                @click="runGenerate('title')"
              >
                {{ generateLabel('title') }}
              </button>
            </div>
            <v-text-field
              v-model="lessonTitle"
              :placeholder="$t('teacher.lessons.titlePlaceholder')"
              variant="outlined"
              density="comfortable"
              hide-details
              class="add-lesson-field add-lesson-field--plain"
            />
          </div>

          <div class="add-lesson-field-block">
            <div class="add-lesson-field-header">
              <span class="add-lesson-field-label">{{ $t('teacher.labels.lessonDescription') }}</span>
              <button
                type="button"
                class="add-lesson-field-generate"
                :disabled="!!generating"
                @click="runGenerate('description')"
              >
                {{ generateLabel('description') }}
              </button>
            </div>
            <p class="add-lesson-field-helper">{{ $t('teacher.lessons.descHelper') }}</p>
            <v-textarea
              v-model="lessonDescription"
              :placeholder="$t('teacher.lessons.descPlaceholder')"
              variant="outlined"
              rows="3"
              auto-grow
              hide-details
              class="add-lesson-field add-lesson-field--plain"
            />
          </div>

          <button
            type="button"
            class="add-lesson-generate-both"
            :disabled="!!generating"
            @click="runGenerate('both')"
          >
            {{ generateBothLabel() }}
          </button>
        </div>
      </section>

      <section class="add-lesson-section" aria-labelledby="add-lesson-source-title">
        <div class="add-lesson-section__head">
          <h3 id="add-lesson-source-title" class="add-lesson-section__title">{{ $t('teacher.lessons.sourceSection') }}</h3>
        </div>

        <LessonSourcePanel
          v-model:source-type="sourceType"
          v-model:video-file="videoPreviewFile"
          v-model:video-url="videoUrl"
          v-model:pdf-file="pdfPreviewFile"
          :pdf-page-count="pdfPageCount"
          :upload-progress="uploadProgress"
          @clear-video="clearVideo"
          @clear-pdf="clearPdf"
        />
      </section>

      <LessonAiProcessingCard />

      <section class="add-lesson-section add-lesson-section--compact" aria-labelledby="add-lesson-publish-title">
        <div class="add-lesson-section__head">
          <h3 id="add-lesson-publish-title" class="add-lesson-section__title">{{ $t('teacher.lessons.publishSection') }}</h3>
        </div>
        <p class="add-lesson-publish__hint">
          {{ $t('teacher.lessons.addHint') }}
        </p>
      </section>
    </div>

    <template #footer>
      <v-btn
        class="add-lesson-workspace__cancel"
        variant="text"
        :disabled="saving"
        @click="close"
      >
        {{ $t('common.cancel') }}
      </v-btn>
      <v-btn
        class="btn-glow add-lesson-workspace__submit"
        rounded="lg"
        :loading="saving"
        @click="submit"
      >
        {{ $t('teacher.actions.saveLesson') }}
        <v-icon end>mdi-arrow-left</v-icon>
      </v-btn>
    </template>
  </LessonWorkspaceScreen>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import LessonWorkspaceScreen from './LessonWorkspaceScreen.vue'
import LessonAiProcessingCard from './lessons/LessonAiProcessingCard.vue'
import LessonSourcePanel from './lessons/LessonSourcePanel.vue'
import { createCourseLesson } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { countPdfPagesFromFile } from '../../utils/pdfPageCount.js'
import { generateLessonMetadata, suggestDescriptionFromTitle } from '../../utils/lessonMetadataGenerate.js'
import { MAX_PDF_SIZE_BYTES, ACCEPTED_PDF_TYPES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'
import { useToast } from '../../composables/useToast.js'
import '../../assets/styles/add-lesson-workspace.css'
import '../../assets/styles/teacher-typography.css'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  courseId: { type: [Number, String], required: true },
})
const emit = defineEmits(['update:modelValue', 'uploaded'])

const { showSuccess, showError, showInfo } = useToast()

const lessonTitle = ref('')
const lessonDescription = ref('')
const sourceType = ref('upload-video')
const videoPreviewFile = ref(null)
const videoUrl = ref('')
const pdfPreviewFile = ref(null)
const pdfPageCount = ref(0)
const saving = ref(false)
const error = ref('')
const generating = ref('')
const uploadProgress = ref(0)

function generateLabel(target) {
  return generating.value === target ? t('teacher.lessons.generating') : t('teacher.lessons.generate')
}

function generateBothLabel() {
  return generating.value === 'both' ? t('teacher.lessons.generating') : t('teacher.lessons.generateTitleDesc')
}

function clearVideo() {
  videoPreviewFile.value = null
}

function clearPdf() {
  pdfPreviewFile.value = null
  pdfPageCount.value = 0
}

watch(pdfPreviewFile, async (file) => {
  pdfPageCount.value = 0
  if (!file) return
  if (!ACCEPTED_PDF_TYPES.includes(file.type) && !file.name?.toLowerCase().endsWith('.pdf')) {
    error.value = t('teacher.lessons.fileMustBePdf')
    pdfPreviewFile.value = null
    return
  }
  if (file.size > MAX_PDF_SIZE_BYTES) {
    error.value = t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL })
    pdfPreviewFile.value = null
    return
  }
  try {
    pdfPageCount.value = await countPdfPagesFromFile(file)
  } catch {
    pdfPageCount.value = 0
  }
})

async function runGenerate(target) {
  generating.value = target
  error.value = ''
  try {
    if (target === 'description') {
      if (!lessonTitle.value.trim()) {
        error.value = t('teacher.lessons.enterTitleFirst')
        return
      }
      lessonDescription.value = suggestDescriptionFromTitle(lessonTitle.value.trim())
      return
    }

    const result = await generateLessonMetadata({
      videoFile: sourceType.value === 'upload-video' ? videoPreviewFile.value : null,
      videoUrl: sourceType.value === 'video-link' ? videoUrl.value : '',
      pdfFile: sourceType.value === 'pdf' ? pdfPreviewFile.value : null,
      target: target === 'both' ? 'both' : 'title',
    })

    if (result.title) lessonTitle.value = result.title
    if (result.description) lessonDescription.value = result.description
  } catch (e) {
    const msg = e?.message || t('teacher.lessons.generateFailed')
    error.value = msg
    showError(msg)
  } finally {
    generating.value = ''
  }
}

function close() {
  if (!saving.value) emit('update:modelValue', false)
}

function reset() {
  lessonTitle.value = ''
  lessonDescription.value = ''
  sourceType.value = 'upload-video'
  videoPreviewFile.value = null
  videoUrl.value = ''
  pdfPreviewFile.value = null
  pdfPageCount.value = 0
  uploadProgress.value = 0
  error.value = ''
  generating.value = ''
}

function hasValidSource() {
  if (sourceType.value === 'upload-video') return Boolean(videoPreviewFile.value)
  if (sourceType.value === 'video-link') return Boolean(videoUrl.value.trim())
  if (sourceType.value === 'pdf') return Boolean(pdfPreviewFile.value)
  return false
}

async function submit() {
  if (!lessonTitle.value.trim()) {
    error.value = t('teacher.lessons.enterTitle')
    return
  }
  if (!hasValidSource()) {
    if (sourceType.value === 'video-link') {
      error.value = t('teacher.lessons.enterValidLink')
    } else if (sourceType.value === 'pdf') {
      error.value = t('teacher.lessons.uploadPdfRequired')
    } else {
      error.value = t('teacher.lessons.uploadVideoFile')
    }
    return
  }

  if (sourceType.value === 'video-link') {
    try {
      // eslint-disable-next-line no-new
      new URL(videoUrl.value.trim())
    } catch {
      error.value = t('teacher.lessons.linkInvalid')
      return
    }
  }

  const video = sourceType.value === 'upload-video' ? videoPreviewFile.value : null
  const pdf = sourceType.value === 'pdf' ? pdfPreviewFile.value : null
  const externalVideoUrl =
    sourceType.value === 'video-link' ? videoUrl.value.trim() : null

  saving.value = true
  uploadProgress.value = 0
  error.value = ''
  try {
    const lesson = await createCourseLesson(
      Number(props.courseId),
      {
        title: lessonTitle.value.trim(),
        description: lessonDescription.value.trim() || null,
        video,
        pdf,
        videoUrl: externalVideoUrl,
      },
      (pct) => {
        uploadProgress.value = pct
      },
    )
    uploadProgress.value = 100
    showSuccess(t('teacher.status.lessonSaved'))
    if (pdf || video) showInfo(t('teacher.status.processingAi'))
    emit('uploaded', lesson)
    reset()
    emit('update:modelValue', false)
  } catch (e) {
    const msg = getErrorMessage(e, t('teacher.errors.saveLesson'))
    error.value = msg
    showError(msg)
  } finally {
    saving.value = false
    uploadProgress.value = 0
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) reset()
  },
)
</script>
