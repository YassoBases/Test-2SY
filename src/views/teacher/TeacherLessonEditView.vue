<template>
  <TeacherWorkspaceShell mode="page" class="teacher-lesson-edit slide-up-enter-active">
    <TeacherHero
      variant="compact"
      :eyebrow="$t('teacher.actions.editContent')"
      :title="heroTitle"
      :subtitle="$t('teacher.lessons.editSubtitle')"
    />

    <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">
      {{ error }}
      <div v-if="!loading" class="mt-3">
        <TeacherButton variant="tonal" size="small" @click="load">
          {{ $t('teacher.actions.retry') }}
        </TeacherButton>
      </div>
    </v-alert>

    <v-progress-linear v-if="loading" indeterminate color="primary" />

    <TeacherEmptyStateCard
      v-else-if="!lesson && !error"
      icon="mdi-book-open-page-variant"
      :title="$t('teacher.lessons.loadFailed')"
      :action-label="$t('teacher.actions.retry')"
      @action="load"
    />

    <TeacherForm v-else-if="lesson" lesson>
      <TeacherFormSection variant="lesson" stack :title="$t('teacher.lessons.infoSection')">
        <TeacherFormField mode="plain" :label="$t('teacher.lessons.titleRequiredLabel')">
          <v-text-field
            v-model="form.title"
            :placeholder="$t('teacher.lessons.titlePlaceholder')"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </TeacherFormField>

        <TeacherFormField
          mode="plain"
          :label="$t('teacher.labels.lessonDescription')"
          :helper-before="$t('teacher.lessons.descHelper')"
        >
          <v-textarea
            v-model="form.description"
            :placeholder="$t('teacher.lessons.descPlaceholder')"
            variant="outlined"
            rows="3"
            auto-grow
            hide-details
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherWarningCard
        v-if="willNeedReprocessing"
        variant="warning"
        :title="$t('teacher.status.needsAiReprocess')"
        :message="$t('teacher.lessons.videoReplaceWarning')"
      />

      <TeacherFormSection variant="lesson" stack :title="$t('teacher.lessons.contentSection')">
        <LessonContentEditorCard
          kind="video"
          :label="$t('teacher.labels.video')"
          icon="mdi-play-circle"
          icon-color="secondary"
          accept="video/*"
          :has-current="initialHasVideo"
          :current-url="videoCurrentUrl"
          :current-filename="videoFilename"
          :removed="flags.removeVideo"
          :replacement-file="files.video"
          @remove="flags.removeVideo = true"
          @undo-remove="flags.removeVideo = false"
          @replace="setFile('video', $event)"
          @clear-replace="clearFile('video')"
        />

        <LessonContentEditorCard
          kind="pdf"
          :label="$t('teacher.labels.pdf')"
          icon="mdi-file-pdf-box"
          icon-color="primary"
          accept="application/pdf,.pdf"
          :has-current="initialHasPdf"
          :current-url="pdfCurrentUrl"
          :current-filename="pdfFilename"
          :removed="flags.removePdf"
          :replacement-file="files.pdf"
          @remove="flags.removePdf = true"
          @undo-remove="flags.removePdf = false"
          @replace="setFile('pdf', $event)"
          @clear-replace="clearFile('pdf')"
          @validation-error="error = $event"
        />

        <LessonContentEditorCard
          kind="audio"
          :label="$t('teacher.labels.audioFile')"
          icon="mdi-volume-high"
          icon-color="info"
          accept="audio/*"
          :has-current="initialHasAudio"
          :current-url="audioCurrentUrl"
          :current-filename="audioFilename"
          :removed="flags.removeAudio"
          :replacement-file="files.audio"
          @remove="flags.removeAudio = true"
          @undo-remove="flags.removeAudio = false"
          @replace="setFile('audio', $event)"
          @clear-replace="clearFile('audio')"
        />
      </TeacherFormSection>

      <TeacherFormSection variant="compact" :title="$t('teacher.lessons.publishSection')">
        <TeacherPublishField
          v-model="form.isVisible"
          mode="inline"
          :label="$t('teacher.labels.publishedVisible')"
          :hint="$t('teacher.lessons.publishHint')"
        />
      </TeacherFormSection>
    </TeacherForm>

    <template v-if="lesson && !loading" #footer>
      <TeacherButtonGroup align="split">
        <TeacherButton variant="ghost" :disabled="saving" :to="previewLink">
          {{ $t('common.cancel') }}
        </TeacherButton>
        <TeacherButton
          variant="primary"
          :loading="saving"
          :disabled="!lesson"
          @click="save"
        >
          {{ $t('teacher.actions.saveChanges') }}
          <v-icon end>mdi-arrow-left</v-icon>
        </TeacherButton>
      </TeacherButtonGroup>
    </template>
  </TeacherWorkspaceShell>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute, useRouter } from 'vue-router'
import LessonContentEditorCard from '../../components/teacher/LessonContentEditorCard.vue'
import {
  TeacherWorkspaceShell,
  TeacherHero,
  TeacherForm,
  TeacherFormSection,
  TeacherFormField,
  TeacherPublishField,
  TeacherWarningCard,
  TeacherEmptyStateCard,
  TeacherButton,
  TeacherButtonGroup,
} from '../../components/teacher/design-system/index.js'
import { fetchTeacherLessonPreview, updateTeacherLessonContent } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { MAX_PDF_SIZE_BYTES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'
import { mediaUrl } from '../../utils/media.js'
import { useToast } from '../../composables/useToast.js'

const route = useRoute()
const router = useRouter()
const { showSuccess, showError, showInfo } = useToast()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const lesson = ref(null)
let loadSeq = 0
let isActive = true

const form = reactive({
  title: '',
  description: '',
  isVisible: true,
})

const flags = reactive({
  removeVideo: false,
  removePdf: false,
  removeAudio: false,
})

const files = reactive({
  video: null,
  pdf: null,
  audio: null,
})

const initialHasVideo = ref(false)
const initialHasPdf = ref(false)
const initialHasAudio = ref(false)

const courseId = computed(() => Number(route.params.courseId))
const lessonId = computed(() => Number(route.params.lessonId))

const heroTitle = computed(() => form.title?.trim() || lesson.value?.title?.trim() || t('teacher.actions.editLesson'))

const routeIdsValid = computed(
  () => Number.isFinite(courseId.value) && courseId.value > 0
    && Number.isFinite(lessonId.value) && lessonId.value > 0,
)

const previewLink = computed(() => ({
  name: 'teacher-lesson-preview',
  params: { courseId: courseId.value, lessonId: lessonId.value },
}))

const videoCurrentUrl = computed(() => (flags.removeVideo ? '' : mediaUrl(lesson.value?.video_url)))
const pdfCurrentUrl = computed(() => (flags.removePdf ? '' : mediaUrl(lesson.value?.pdf_url)))
const audioCurrentUrl = computed(() => (flags.removeAudio ? '' : mediaUrl(lesson.value?.audio_url)))

function assetFilename(type) {
  const asset = lesson.value?.assets?.find((a) => a.asset_type === type)
  return asset?.original_filename || ''
}

const videoFilename = computed(() => assetFilename('video'))
const pdfFilename = computed(() => assetFilename('pdf'))
const audioFilename = computed(() => assetFilename('audio'))

const willNeedReprocessing = computed(() => {
  const hadPdf = initialHasPdf.value
  const pdfTouched = flags.removePdf || !!files.pdf
  const videoTouched = flags.removeVideo || !!files.video
  return hadPdf && (pdfTouched || videoTouched)
})

function setFile(kind, file) {
  if (kind === 'pdf' && file.size > MAX_PDF_SIZE_BYTES) {
    error.value = t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL })
    return
  }
  files[kind] = file
  flags[`remove${kind.charAt(0).toUpperCase()}${kind.slice(1)}`] = false
}

function clearFile(kind) {
  files[kind] = null
}

function effectiveHas(kind) {
  const initial = kind === 'video' ? initialHasVideo.value : kind === 'pdf' ? initialHasPdf.value : initialHasAudio.value
  const removed = flags[`remove${kind.charAt(0).toUpperCase()}${kind.slice(1)}`]
  const replaced = !!files[kind]
  return (initial && !removed) || replaced
}

function resetContentFlags() {
  flags.removeVideo = false
  flags.removePdf = false
  flags.removeAudio = false
  files.video = null
  files.pdf = null
  files.audio = null
}

async function load() {
  const seq = ++loadSeq
  loading.value = true
  error.value = ''
  lesson.value = null
  resetContentFlags()

  if (!routeIdsValid.value) {
    if (!isActive || seq !== loadSeq) return
    error.value = t('teacher.lessons.invalidId')
    loading.value = false
    return
  }

  try {
    const data = await fetchTeacherLessonPreview(courseId.value, lessonId.value)
    if (!isActive || seq !== loadSeq) return

    lesson.value = data
    form.title = data.title || ''
    form.description = data.description || ''
    form.isVisible = data.is_visible !== false
    initialHasVideo.value = !!data.has_video
    initialHasPdf.value = !!data.has_pdf
    initialHasAudio.value = !!data.has_audio
  } catch (e) {
    if (!isActive || seq !== loadSeq) return
    error.value = getErrorMessage(e, t('teacher.errors.loadLesson'))
    lesson.value = null
  } finally {
    if (isActive && seq === loadSeq) loading.value = false
  }
}

async function save() {
  if (!String(form.title || '').trim()) {
    error.value = t('teacher.lessons.titleRequired')
    return
  }
  if (!effectiveHas('video') && !effectiveHas('pdf') && !effectiveHas('audio')) {
    error.value = t('teacher.lessons.needsMediaFull')
    return
  }

  saving.value = true
  error.value = ''
  try {
    const result = await updateTeacherLessonContent(courseId.value, lessonId.value, {
      title: form.title.trim(),
      description: form.description.trim() || null,
      isVisible: form.isVisible,
      removeVideo: flags.removeVideo,
      removePdf: flags.removePdf,
      removeAudio: flags.removeAudio,
      video: files.video,
      pdf: files.pdf,
      audio: files.audio,
    })
    if (result.needs_reprocessing) {
      showInfo(t('teacher.lessons.savedNeedsReprocessAi'))
    } else {
      showSuccess(t('teacher.status.changesSaved'))
    }
    await router.push(previewLink.value)
  } catch (e) {
    const msg = getErrorMessage(e, t('teacher.errors.save'))
    error.value = msg
    showError(msg)
  } finally {
    saving.value = false
  }
}

watch(
  () => [route.params.courseId, route.params.lessonId],
  () => load(),
  { immediate: true },
)

onBeforeUnmount(() => {
  isActive = false
  loadSeq += 1
})
</script>
