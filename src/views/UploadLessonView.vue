<template>
  <LessonWorkspaceScreen
    :open="true"
    :eyebrow="t('dashboard.uploadLesson.eyebrow')"
    :title="t('dashboard.uploadLesson.title')"
    :subtitle="t('dashboard.uploadLesson.subtitle')"
    :busy="publishing"
    @close="goBack"
  >
    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg" closable @click:close="loadError = ''">
      {{ loadError }}
    </v-alert>

    <v-alert
      v-if="!voiceReady && !loadingVoice"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
      density="comfortable"
    >
      {{ t('dashboard.uploadLesson.voiceSampleHint') }}
      <router-link :to="{ name: 'teacher-profile' }" class="text-secondary font-weight-bold">
        {{ t('dashboard.uploadLesson.voiceSampleLink') }}
      </router-link>
      {{ t('dashboard.uploadLesson.voiceSampleSuffix') }}
    </v-alert>

    <v-card class="lesson-workspace-panel pa-5 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-4">
        <v-icon color="secondary" class="me-2">mdi-book-edit</v-icon>
        {{ t('dashboard.uploadLesson.lessonDetails') }}
      </h3>
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-select
            v-model="grade"
            :items="gradeItems"
            item-title="label"
            item-value="value"
            :label="t('dashboard.uploadLesson.gradeLabel')"
            variant="outlined"
            density="comfortable"
            :loading="loadingContext"
            @update:model-value="onGradeChange"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            v-model="subjectId"
            :items="subjectItems"
            item-title="name_ar"
            item-value="id"
            :label="t('dashboard.uploadLesson.subjectLabel')"
            variant="outlined"
            density="comfortable"
            :loading="loadingContext"
            :disabled="!grade"
          />
        </v-col>
        <v-col cols="12">
          <v-text-field v-model="title" :label="t('dashboard.uploadLesson.lessonTitleLabel')" variant="outlined" density="comfortable" />
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="description" :label="t('dashboard.uploadLesson.descriptionLabel')" variant="outlined" rows="2" auto-grow />
        </v-col>
      </v-row>
    </v-card>

    <v-card class="lesson-workspace-panel pa-5 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-1">
        <v-icon color="secondary" class="me-2">mdi-video</v-icon>
        {{ t('dashboard.uploadLesson.videoLesson') }}
        <v-chip size="x-small" variant="tonal" class="ms-2">{{ t('dashboard.uploadLesson.optional') }}</v-chip>
      </h3>
      <v-file-input
        v-model="videoFile"
        :label="t('dashboard.uploadLesson.chooseVideo')"
        prepend-icon="mdi-video"
        accept="video/*"
        variant="outlined"
        density="comfortable"
        show-size
        clearable
        class="mb-4"
        @update:model-value="onVideoChange"
      />
      <VideoPreviewCard v-if="videoPreviewFile" :file="videoPreviewFile" @remove="clearVideo" />
    </v-card>

    <v-card class="lesson-workspace-panel pa-5 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-4">
        <v-icon color="secondary" class="me-2">mdi-file-pdf-box</v-icon>
        {{ t('dashboard.uploadLesson.pdfFile') }}
        <v-chip size="x-small" variant="tonal" class="ms-2">{{ t('dashboard.uploadLesson.optional') }}</v-chip>
      </h3>
      <UploadCard
        :file="pdfFile"
        :uploading="false"
        :progress="0"
        :error="pdfError"
        :subtitle="t('common.upload.pdfSubtitle')"
        :show-header="false"
        opaque
        @select="onPdfSelect"
        @remove="clearPdf"
        @dismiss-error="pdfError = ''"
      />
      <PdfPreviewCard
        v-if="pdfFile"
        :file="pdfFile"
        :page-count="estimatedPages"
        class="mt-4"
      />
    </v-card>

    <v-card class="lesson-workspace-panel pa-5 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">
        <v-icon color="secondary" class="me-2">mdi-waveform</v-icon>
        {{ t('dashboard.uploadLesson.voiceFromProfile') }}
      </h3>
      <p class="text-body-2 text-medium-emphasis mb-3">
        {{ t('dashboard.uploadLesson.voiceAutoUsed') }}
      </p>
      <v-chip :color="voiceReady ? 'success' : 'warning'" variant="tonal" prepend-icon="mdi-microphone">
        {{ voiceReady ? t('dashboard.uploadLesson.voiceReady') : t('dashboard.uploadLesson.voiceNotUploaded') }}
      </v-chip>
    </v-card>

    <v-card v-if="publishedLessonId" class="lesson-workspace-panel pa-5 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-4">
        <v-icon color="secondary" class="me-2">mdi-creation</v-icon>
        {{ t('dashboard.uploadLesson.smartProcessingStatus') }}
        <v-progress-circular v-if="!publishStatus?.complete" indeterminate size="20" width="2" color="secondary" class="ms-2" />
      </h3>
      <v-timeline v-if="publishStatus?.steps?.length" side="end" density="compact" truncate-line="both">
        <v-timeline-item
          v-for="step in publishStatus.steps"
          :key="step.key"
          :dot-color="stepColor(step)"
          size="small"
          :icon="stepIcon(step)"
        >
          <div class="text-body-2" :class="step.done ? 'font-weight-bold text-secondary' : 'text-medium-emphasis'">
            {{ step.label }}
          </div>
          <div v-if="step.error" class="text-caption text-error mt-1">{{ step.error }}</div>
        </v-timeline-item>
      </v-timeline>
    </v-card>

    <v-alert v-if="submitError" type="error" variant="tonal" class="mb-4 rounded-lg" closable @click:close="submitError = ''">
      {{ submitError }}
    </v-alert>

    <v-alert v-if="showValidation && !canSubmit" type="warning" variant="tonal" class="mb-4 rounded-lg" density="comfortable">
      {{ t('dashboard.uploadLesson.completeRequirements') }}
    </v-alert>

    <template #footer>
      <v-btn variant="outlined" size="large" :to="{ name: 'teacher-dashboard' }">{{ t('common.cancel') }}</v-btn>
      <v-btn
        v-if="publishedLessonId && publishStatus?.complete"
        variant="tonal"
        size="large"
        prepend-icon="mdi-view-dashboard"
        :to="{ name: 'teacher-dashboard' }"
      >
        {{ t('dashboard.uploadLesson.dashboard') }}
      </v-btn>
      <v-btn
        color="primary"
        size="large"
        class="btn-glow"
        :disabled="publishing || !!publishedLessonId"
        :loading="publishing"
        prepend-icon="mdi-cloud-upload"
        @click="onPublishClick"
      >
        {{ t('dashboard.uploadLesson.uploadLesson') }}
      </v-btn>
    </template>
  </LessonWorkspaceScreen>

  <LessonWorkspaceScreen
    :open="confirmOpen"
    layered
    :title="t('dashboard.uploadLesson.confirmTitle')"
    :subtitle="t('dashboard.uploadLesson.confirmSubtitle')"
    :busy="publishing"
    @close="confirmOpen = false"
  >
    <v-card class="lesson-workspace-panel pa-5" variant="flat">
      <v-list density="comfortable" class="bg-transparent">
        <v-list-item prepend-icon="mdi-format-title" :title="title || '—'" />
        <v-list-item prepend-icon="mdi-school" :title="gradeLabel" />
        <v-list-item prepend-icon="mdi-book-education" :title="subjectLabel" />
        <v-list-item prepend-icon="mdi-video" :title="videoLabel" />
        <v-list-item prepend-icon="mdi-file-pdf-box" :title="pdfLabel" />
      </v-list>
    </v-card>

    <template #footer>
      <v-btn variant="outlined" size="large" :disabled="publishing" @click="confirmOpen = false">{{ t('dashboard.uploadLesson.back') }}</v-btn>
      <v-btn color="primary" size="large" class="btn-glow" :loading="publishing" @click="submitLesson">
        {{ t('dashboard.uploadLesson.confirmUpload') }}
      </v-btn>
    </template>
  </LessonWorkspaceScreen>

  <LoadingOverlay
    :show="publishing"
    :progress="uploadProgress"
    :title="t('dashboard.uploadLesson.uploadingTitle')"
    :subtitle="t('dashboard.uploadLesson.uploadingSubtitle')"
  />
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import LessonWorkspaceScreen from '../components/teacher/LessonWorkspaceScreen.vue'
import UploadCard from '../components/common/UploadCard.vue'
import PdfPreviewCard from '../components/teacher/PdfPreviewCard.vue'
import VideoPreviewCard from '../components/teacher/VideoPreviewCard.vue'
import LoadingOverlay from '../components/common/LoadingOverlay.vue'
import { fetchCourseFormContext, publishLesson, fetchLessonPublishStatus } from '../api/teacherCourses.js'
import { fetchTeacherVoiceProfile } from '../api/teacher.js'
import { MAX_PDF_SIZE_LABEL, MAX_PDF_SIZE_BYTES, ACCEPTED_PDF_TYPES, ACADEMIC_GRADES, ROUTES } from '../constants/app.js'
import { getErrorMessage } from '../api/client.js'
import { countPdfPagesFromFile } from '../utils/pdfPageCount.js'
import { useToast } from '../composables/useToast.js'

const maxSizeLabel = MAX_PDF_SIZE_LABEL
const { t } = useI18n()
const { showSuccess, showError, showInfo } = useToast()
const router = useRouter()

function goBack() {
  router.push(ROUTES.TEACHER_GRADES)
}

const grade = ref(null)
const subjectId = ref(null)
const title = ref('')
const description = ref('')
const videoFile = ref(null)
const videoPreviewFile = ref(null)
const pdfFile = ref(null)
const pdfError = ref('')
const estimatedPages = ref(0)

const grades = ref([...ACADEMIC_GRADES])
const subjects = ref([])
const loadingContext = ref(false)
const loadError = ref('')

const voiceReady = ref(false)
const loadingVoice = ref(true)

const publishing = ref(false)
const submitError = ref('')
const uploadProgress = ref(0)
const showValidation = ref(false)
const confirmOpen = ref(false)

const publishedLessonId = ref(null)
const publishStatus = ref(null)
let statusPollTimer = null

const gradeItems = computed(() => grades.value.map((g) => ({ label: t('dashboard.uploadLesson.gradeOption', { grade: g }), value: g })))
const subjectItems = computed(() => subjects.value)
const gradeLabel = computed(() => (grade.value ? t('dashboard.uploadLesson.gradeOption', { grade: grade.value }) : '—'))
const subjectLabel = computed(() => subjects.value.find((s) => s.id === subjectId.value)?.name_ar || '—')

function pickFile(input) {
  if (!input) return null
  return Array.isArray(input) ? input[0] : input
}

const hasVideo = computed(() => !!videoPreviewFile.value)
const hasPdf = computed(() => !!pdfFile.value)
const canSubmit = computed(() => grade.value && subjectId.value && title.value.trim() && (hasVideo.value || hasPdf.value))
const videoLabel = computed(() => (hasVideo.value ? videoPreviewFile.value?.name : t('dashboard.uploadLesson.noVideo')))
const pdfLabel = computed(() => (hasPdf.value ? pdfFile.value?.name : t('dashboard.uploadLesson.noPdf')))

function onVideoChange(input) {
  videoPreviewFile.value = pickFile(input)
}

function clearVideo() {
  videoFile.value = null
  videoPreviewFile.value = null
}

async function loadVoiceStatus() {
  loadingVoice.value = true
  try {
    const profile = await fetchTeacherVoiceProfile()
    voiceReady.value = !!profile?.has_ready_profile
  } catch {
    voiceReady.value = false
  } finally {
    loadingVoice.value = false
  }
}

async function loadContext(g) {
  if (!g) return
  loadingContext.value = true
  loadError.value = ''
  try {
    const ctx = await fetchCourseFormContext(g)
    grades.value = ctx.grades?.length ? ctx.grades : [...ACADEMIC_GRADES]
    subjects.value = ctx.subjects || []
    if (!subjects.value.find((s) => s.id === subjectId.value)) {
      subjectId.value = subjects.value[0]?.id ?? null
    }
  } catch (e) {
    loadError.value = getErrorMessage(e, t('dashboard.uploadLesson.loadSubjectsFailed'))
  } finally {
    loadingContext.value = false
  }
}

function onGradeChange(g) {
  loadContext(g)
}

async function onPdfSelect(file) {
  pdfError.value = ''
  if (!file) {
    pdfFile.value = null
    estimatedPages.value = 0
    return
  }
  if (!ACCEPTED_PDF_TYPES.includes(file.type) && !file.name?.toLowerCase().endsWith('.pdf')) {
    pdfError.value = t('dashboard.uploadLesson.pdfMustBePdf')
    return
  }
  if (file.size > MAX_PDF_SIZE_BYTES) {
    pdfError.value = t('dashboard.uploadLesson.fileTooLarge', { size: maxSizeLabel })
    return
  }
  pdfFile.value = file
  try {
    estimatedPages.value = await countPdfPagesFromFile(file)
  } catch {
    estimatedPages.value = 0
  }
}

function clearPdf() {
  pdfFile.value = null
  pdfError.value = ''
  estimatedPages.value = 0
}

function stepColor(step) {
  if (step.error) return 'error'
  if (step.done) return 'success'
  if (step.active) return 'secondary'
  return 'grey-darken-2'
}

function stepIcon(step) {
  if (step.done) return 'mdi-check'
  if (step.active) return 'mdi-loading'
  return undefined
}

function stopStatusPoll() {
  if (statusPollTimer) {
    clearInterval(statusPollTimer)
    statusPollTimer = null
  }
}

async function refreshPublishStatus() {
  if (!publishedLessonId.value) return
  try {
    publishStatus.value = await fetchLessonPublishStatus(publishedLessonId.value)
    if (publishStatus.value?.complete) {
      stopStatusPoll()
      showSuccess(t('dashboard.uploadLesson.processingComplete'))
    }
  } catch {
    /* ignore transient poll errors */
  }
}

function startStatusPoll() {
  stopStatusPoll()
  statusPollTimer = setInterval(refreshPublishStatus, 2500)
}

function onPublishClick() {
  showValidation.value = true
  if (!canSubmit.value) return
  confirmOpen.value = true
}

async function submitLesson() {
  confirmOpen.value = false
  if (!canSubmit.value) return

  publishing.value = true
  submitError.value = ''
  uploadProgress.value = 0

  try {
    const result = await publishLesson(
      {
        grade: grade.value,
        subjectId: subjectId.value,
        title: title.value.trim(),
        description: description.value.trim() || undefined,
        video: videoPreviewFile.value,
        pdf: pdfFile.value,
      },
      (pct) => {
        uploadProgress.value = pct
      },
    )

    showSuccess(t('dashboard.uploadLesson.uploadSuccess'))
    if (result.ai_processing_scheduled) {
      showInfo(t('dashboard.uploadLesson.aiProcessingStarted'))
    }

    publishedLessonId.value = result.lesson_id
    publishStatus.value = {
      complete: false,
      steps: [
        { key: 'saved', label: result.message || t('dashboard.uploadLesson.uploadSaved'), done: true },
        ...(result.ai_processing_scheduled
          ? [{ key: 'pdf_ai', label: t('dashboard.uploadLesson.pdfProcessing'), done: false, active: true }]
          : []),
      ],
    }

    await refreshPublishStatus()
    startStatusPoll()
  } catch (e) {
    const msg = getErrorMessage(e, t('dashboard.uploadLesson.uploadFailed'))
    submitError.value = msg
    showError(msg)
  } finally {
    publishing.value = false
  }
}

onMounted(() => {
  loadVoiceStatus()
  if (grades.value.length) {
    grade.value = grades.value[0]
    loadContext(grade.value)
  }
})
onUnmounted(stopStatusPoll)
</script>
