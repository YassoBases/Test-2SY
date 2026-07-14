<template>
  <div class="lesson-source-panel">
    <div class="lesson-source-panel__type-row" role="radiogroup" :aria-label="$t('teacher.labels.sourceType')">
      <button
        v-for="option in sourceOptions"
        :key="option.value"
        type="button"
        class="lesson-source-panel__type"
        :class="{ 'lesson-source-panel__type--active': sourceType === option.value }"
        role="radio"
        :aria-checked="sourceType === option.value"
        @click="setSourceType(option.value)"
      >
        <span class="lesson-source-panel__type-radio" aria-hidden="true" />
        <v-icon :icon="option.icon" size="18" class="lesson-source-panel__type-icon" />
        <span class="lesson-source-panel__type-label">{{ option.label }}</span>
      </button>
    </div>

    <!-- Uploaded video -->
    <div v-if="sourceType === 'upload-video'" class="lesson-source-panel__pane">
      <p class="lesson-source-panel__pane-hint">{{ $t('teacher.actions.dragVideo') }}</p>
      <div
        class="lesson-source-panel__dropzone"
        :class="dropzoneClass('video', !!videoFile, videoDragOver)"
        role="button"
        tabindex="0"
        @click="triggerPick('video')"
        @keydown.enter.space.prevent="triggerPick('video')"
        @dragenter.prevent="videoDragOver = true"
        @dragover.prevent="videoDragOver = true"
        @dragleave.prevent="videoDragOver = false"
        @drop.prevent="onVideoDrop"
      >
        <template v-if="!videoFile">
          <v-icon size="40" class="lesson-source-panel__dropzone-icon">mdi-cloud-upload-outline</v-icon>
          <p class="lesson-source-panel__dropzone-title">{{ $t('teacher.lessons.dragDropGeneric') }}</p>
          <p class="lesson-source-panel__dropzone-sub">{{ $t('common.or') }} <span class="lesson-source-panel__dropzone-cta">{{ $t('teacher.actions.chooseFile') }}</span></p>
          <p class="lesson-source-panel__dropzone-formats">MP4 · MOV · AVI · MKV</p>
        </template>
        <template v-else>
          <div class="lesson-source-panel__file-ready">
            <v-icon size="28" class="lesson-source-panel__dropzone-icon">mdi-check-circle-outline</v-icon>
            <p class="lesson-source-panel__dropzone-title">{{ videoFile.name }}</p>
            <p class="lesson-source-panel__dropzone-sub">{{ formatFileSize(videoFile.size) }}</p>
          </div>
          <div class="lesson-source-panel__dropzone-actions">
            <v-btn size="small" variant="tonal" rounded="lg" @click.stop="triggerPick('video')">{{ $t('common.update') }}</v-btn>
            <v-btn size="small" variant="text" color="error" rounded="lg" @click.stop="$emit('clear-video')">
              {{ $t('common.delete') }}
            </v-btn>
          </div>
        </template>
      </div>

      <VideoPreviewCard
        v-if="videoFile"
        :file="videoFile"
        class="lesson-source-panel__preview"
        @remove="$emit('clear-video')"
      />

      <v-progress-linear
        v-if="uploadProgress > 0 && uploadProgress < 100"
        :model-value="uploadProgress"
        color="primary"
        height="5"
        rounded
        class="lesson-source-panel__progress"
      />
    </div>

    <!-- Video link -->
    <div v-else-if="sourceType === 'video-link'" class="lesson-source-panel__pane">
      <label class="lesson-source-panel__field-label" for="lesson-video-url">{{ $t('teacher.labels.videoLink') }}</label>
      <v-text-field
        id="lesson-video-url"
        :model-value="videoUrl"
        placeholder="https://youtube.com/watch?v=..."
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-link-variant"
        hide-details
        class="add-lesson-field add-lesson-field--plain"
        @update:model-value="onVideoUrlInput"
      />
      <p class="lesson-source-panel__pane-hint lesson-source-panel__pane-hint--inline">
        {{ $t('teacher.lessons.videoLinkFormats') }}
      </p>

      <LessonVideoLinkPreviewCard
        v-if="videoUrl.trim() && (linkPreviewLoading || linkPreview || linkPreviewError)"
        :preview="linkPreview"
        :url="videoUrl"
        :loading="linkPreviewLoading"
        :error="linkPreviewError"
      />
    </div>

    <!-- PDF upload -->
    <div v-else class="lesson-source-panel__pane">
      <p class="lesson-source-panel__pane-hint">{{ $t('teacher.lessons.uploadPdfHint') }}</p>
      <div
        class="lesson-source-panel__dropzone lesson-source-panel__dropzone--pdf"
        :class="dropzoneClass('pdf', !!pdfFile, pdfDragOver)"
        role="button"
        tabindex="0"
        @click="triggerPick('pdf')"
        @keydown.enter.space.prevent="triggerPick('pdf')"
        @dragenter.prevent="pdfDragOver = true"
        @dragover.prevent="pdfDragOver = true"
        @dragleave.prevent="pdfDragOver = false"
        @drop.prevent="onPdfDrop"
      >
        <template v-if="!pdfFile">
          <v-icon size="40" class="lesson-source-panel__dropzone-icon">mdi-file-pdf-box</v-icon>
          <p class="lesson-source-panel__dropzone-title">{{ $t('teacher.lessons.dragPdfDrop') }}</p>
          <p class="lesson-source-panel__dropzone-sub">{{ $t('common.or') }} <span class="lesson-source-panel__dropzone-cta">{{ $t('teacher.actions.chooseFile') }}</span></p>
          <p class="lesson-source-panel__dropzone-formats">{{ $t('teacher.lessons.pdfFormats', { size: maxPdfLabel }) }}</p>
        </template>
        <template v-else>
          <div class="lesson-source-panel__file-ready">
            <v-icon size="32" class="lesson-source-panel__dropzone-icon lesson-source-panel__dropzone-icon--pdf">
              mdi-file-pdf-box
            </v-icon>
            <p class="lesson-source-panel__dropzone-title">{{ pdfFile.name }}</p>
            <p class="lesson-source-panel__dropzone-sub">{{ formatFileSize(pdfFile.size) }}</p>
          </div>
          <div class="lesson-source-panel__dropzone-actions">
            <v-btn size="small" variant="tonal" rounded="lg" @click.stop="triggerPick('pdf')">{{ $t('common.update') }}</v-btn>
            <v-btn size="small" variant="text" color="error" rounded="lg" @click.stop="$emit('clear-pdf')">
              {{ $t('common.delete') }}
            </v-btn>
          </div>
        </template>
      </div>

      <PdfPreviewCard
        v-if="pdfFile"
        :file="pdfFile"
        :page-count="pdfPageCount"
        class="lesson-source-panel__preview"
        @remove="$emit('clear-pdf')"
      />
    </div>

    <input
      ref="videoInput"
      type="file"
      accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/*,.mp4,.mov,.avi,.mkv"
      class="d-none"
      @change="onVideoPick"
    />
    <input ref="pdfInput" type="file" accept="application/pdf,.pdf" class="d-none" @change="onPdfPick" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import VideoPreviewCard from '../VideoPreviewCard.vue'
import PdfPreviewCard from '../PdfPreviewCard.vue'
import LessonVideoLinkPreviewCard from './LessonVideoLinkPreviewCard.vue'
import { formatFileSize } from '../../../utils/format.js'
import { MAX_PDF_SIZE_LABEL } from '../../../constants/app.js'
import { fetchVideoLinkPreview } from '../../../utils/lessonMetadataGenerate.js'

const props = defineProps({
  sourceType: { type: String, default: 'upload-video' },
  videoFile: { type: Object, default: null },
  videoUrl: { type: String, default: '' },
  pdfFile: { type: Object, default: null },
  pdfPageCount: { type: Number, default: 0 },
  uploadProgress: { type: Number, default: 0 },
})

const emit = defineEmits([
  'update:sourceType',
  'update:videoFile',
  'update:videoUrl',
  'update:pdfFile',
  'clear-video',
  'clear-pdf',
])

const maxPdfLabel = MAX_PDF_SIZE_LABEL
const videoDragOver = ref(false)
const pdfDragOver = ref(false)
const videoInput = ref(null)
const pdfInput = ref(null)
const linkPreview = ref(null)
const linkPreviewLoading = ref(false)
const linkPreviewError = ref('')
let linkPreviewTimer = null
let linkPreviewRequest = 0

const sourceOptions = [
  { value: 'upload-video', label: t('teacher.actions.uploadVideo'), icon: 'mdi-video-outline' },
  { value: 'video-link', label: t('teacher.lessons.videoLinkTab'), icon: 'mdi-link-variant' },
  { value: 'pdf', label: t('teacher.lessons.uploadPdfTab'), icon: 'mdi-file-pdf-box' },
]

function setSourceType(next) {
  if (next === props.sourceType) return
  emit('update:sourceType', next)
  if (next !== 'upload-video') emit('clear-video')
  if (next !== 'video-link') {
    emit('update:videoUrl', '')
    clearLinkPreview()
  }
  if (next !== 'pdf') emit('clear-pdf')
}

function dropzoneClass(kind, filled, dragOver) {
  return {
    'lesson-source-panel__dropzone--filled': filled,
    'lesson-source-panel__dropzone--active': dragOver,
    [`lesson-source-panel__dropzone--${kind}`]: true,
  }
}

function triggerPick(kind) {
  if (kind === 'video') videoInput.value?.click()
  else pdfInput.value?.click()
}

const VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']

function isVideoFile(file) {
  if (!file) return false
  if (String(file.type || '').startsWith('video/')) return true
  const name = String(file.name || '').toLowerCase()
  return VIDEO_EXTENSIONS.some((ext) => name.endsWith(ext))
}

function applyVideo(file) {
  if (!isVideoFile(file)) return
  emit('update:videoFile', file)
}

function applyPdf(file) {
  if (!file) return
  const isPdf =
    file.type === 'application/pdf' || String(file.name || '').toLowerCase().endsWith('.pdf')
  if (!isPdf) return
  emit('update:pdfFile', file)
}

function onVideoPick(e) {
  applyVideo(e.target.files?.[0])
  e.target.value = ''
}

function onPdfPick(e) {
  applyPdf(e.target.files?.[0])
  e.target.value = ''
}

function onVideoDrop(e) {
  videoDragOver.value = false
  applyVideo(e.dataTransfer?.files?.[0])
}

function onPdfDrop(e) {
  pdfDragOver.value = false
  applyPdf(e.dataTransfer?.files?.[0])
}

function clearLinkPreview() {
  linkPreview.value = null
  linkPreviewError.value = ''
  linkPreviewLoading.value = false
}

function onVideoUrlInput(value) {
  emit('update:videoUrl', value)
}

async function loadLinkPreview(url) {
  const trimmed = String(url || '').trim()
  if (!trimmed) {
    clearLinkPreview()
    return
  }

  const requestId = ++linkPreviewRequest
  linkPreviewLoading.value = true
  linkPreviewError.value = ''
  linkPreview.value = null

  try {
    const preview = await fetchVideoLinkPreview(trimmed)
    if (requestId !== linkPreviewRequest) return
    linkPreview.value = { ...preview, url: trimmed }
  } catch (e) {
    if (requestId !== linkPreviewRequest) return
    linkPreviewError.value = e?.message || t('teacher.lessons.linkUnrecognized')
    linkPreview.value = null
  } finally {
    if (requestId === linkPreviewRequest) {
      linkPreviewLoading.value = false
    }
  }
}

watch(
  () => props.videoUrl,
  (url) => {
    if (props.sourceType !== 'video-link') return
    if (linkPreviewTimer) clearTimeout(linkPreviewTimer)
    const trimmed = String(url || '').trim()
    if (!trimmed) {
      clearLinkPreview()
      return
    }
    linkPreviewTimer = setTimeout(() => loadLinkPreview(trimmed), 450)
  },
)
</script>
