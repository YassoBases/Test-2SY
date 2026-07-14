<template>
  <div class="teacher-lesson-preview slide-up-enter-active" dir="rtl">
    <PageHeader
      :eyebrow="$t('teacher.lessons.previewEyebrow')"
      :title="lesson?.title || '...'"
      :subtitle="headerSubtitle"
    >
      <template #actions>
        <div class="preview-header-actions">
          <v-btn variant="tonal" :to="backLink">{{ $t('common.back') }}</v-btn>
          <template v-if="!smAndDown">
            <v-btn variant="tonal" color="primary" :to="editLink">{{ $t('common.edit') }}</v-btn>
            <v-btn
              v-if="canReprocess"
              variant="tonal"
              color="warning"
              :loading="reprocessing"
              @click="reprocess"
            >
              {{ $t('teacher.actions.reprocessAi') }}
            </v-btn>
          </template>
          <v-menu v-else location="bottom end">
            <template #activator="{ props: menuProps }">
              <v-btn
                v-bind="menuProps"
                variant="tonal"
                icon="mdi-dots-vertical"
                :aria-label="$t('teacher.actions.moreActions')"
              />
            </template>
            <v-list density="compact" class="preview-header-menu">
              <v-list-item :to="editLink" prepend-icon="mdi-pencil-outline" :title="$t('common.edit')" />
              <v-list-item
                v-if="canReprocess"
                prepend-icon="mdi-refresh"
                :title="$t('teacher.actions.reprocessAi')"
                :disabled="reprocessing"
                @click="reprocess"
              />
            </v-list>
          </v-menu>
        </div>
      </template>
    </PageHeader>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

    <template v-if="lesson && !loading">
      <v-card class="preview-panel pa-5 mb-4" variant="flat">
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <p class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.labels.contentType') }}</p>
            <v-chip size="small" variant="tonal">{{ lesson.content_type_label }}</v-chip>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <p class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.labels.processingStatus') }}</p>
            <v-chip size="small" :color="statusColor(lesson.status, lesson.needs_reprocessing)" variant="tonal">
              {{ statusLabel(lesson.status, lesson.needs_reprocessing) }}
            </v-chip>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <p class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.labels.visibility') }}</p>
            <v-chip size="small" :color="lesson.is_visible ? 'success' : 'warning'" variant="tonal">
              {{ lesson.is_visible ? $t('teacher.status.published') : $t('teacher.status.hidden') }}
            </v-chip>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <p class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.labels.uploadDate') }}</p>
            <p class="text-body-2 mb-0">{{ formatDate(lesson.created_at) }}</p>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <p class="text-caption text-medium-emphasis mb-1">{{ $t('teacher.lessons.studentCompletion') }}</p>
            <p class="text-body-2 mb-0" dir="ltr">{{ lesson.completion_percent }}%</p>
          </v-col>
        </v-row>
        <p v-if="lesson.description" class="text-body-2 mt-4 mb-0">{{ lesson.description }}</p>
        <p v-if="lesson.preview" class="text-body-2 text-medium-emphasis mt-3 mb-0">{{ lesson.preview }}</p>
        <v-alert
          v-if="lesson.needs_reprocessing"
          type="warning"
          variant="tonal"
          density="comfortable"
          class="mt-4 mb-0 rounded-lg"
        >
          {{ $t('teacher.lessons.needsReprocessBanner') }}
        </v-alert>
        <v-alert
          v-if="lesson.error_message"
          type="error"
          variant="tonal"
          density="comfortable"
          class="mt-4 mb-0 rounded-lg"
        >
          {{ lesson.error_message }}
        </v-alert>
      </v-card>

      <v-card class="preview-panel overflow-hidden" variant="flat">
        <v-tabs v-model="activeTab" color="primary" grow>
          <v-tab value="video" :disabled="!lesson.has_video">
            <v-icon start>mdi-play-circle</v-icon>
            {{ $t('teacher.labels.video') }}
          </v-tab>
          <v-tab value="pdf" :disabled="!lesson.has_pdf">
            <v-icon start>mdi-file-pdf-box</v-icon>
            PDF
          </v-tab>
          <v-tab value="audio" :disabled="!lesson.has_audio">
            <v-icon start>mdi-volume-high</v-icon>
            {{ $t('teacher.labels.audio') }}
          </v-tab>
        </v-tabs>
        <v-divider />
        <v-card-text class="pa-5">
          <v-window v-model="activeTab">
            <v-window-item value="video">
              <div v-if="videoSrc" class="media-frame">
                <video :src="videoSrc" controls playsinline class="w-100" />
              </div>
              <p v-else class="text-center text-medium-emphasis pa-8 mb-0">{{ $t('teacher.lessons.noVideo') }}</p>
            </v-window-item>

            <v-window-item value="pdf">
              <template v-if="pdfSrc">
                <div class="d-flex flex-wrap gap-2 mb-4">
                  <v-btn color="primary" variant="tonal" prepend-icon="mdi-open-in-new" :href="pdfSrc" target="_blank" rel="noopener">
                    {{ $t('teacher.actions.openNewTab') }}
                  </v-btn>
                </div>
                <div class="pdf-preview-frame">
                  <iframe :src="pdfSrc" class="pdf-iframe rounded-lg" :title="$t('teacher.actions.openPdfPreview')" />
                </div>
              </template>
              <p v-else class="text-center text-medium-emphasis pa-8 mb-0">{{ $t('teacher.lessons.noPdf') }}</p>
            </v-window-item>

            <v-window-item value="audio">
              <div v-if="audioSrc" class="audio-frame pa-4 rounded-lg">
                <p class="text-body-2 mb-3">{{ $t('teacher.lessons.noAudioPreview') }}</p>
                <audio :src="audioSrc" controls class="w-100" />
              </div>
              <p v-else class="text-center text-medium-emphasis pa-8 mb-0">{{ $t('teacher.lessons.noAudio') }}</p>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>

      <v-alert type="info" variant="tonal" class="mt-4 rounded-lg" density="comfortable">
        {{ $t('teacher.lessons.previewNote') }}
      </v-alert>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute } from 'vue-router'
import { useDisplay } from 'vuetify'
import PageHeader from '../../components/common/PageHeader.vue'
import { fetchTeacherLessonPreview, processCourseLesson } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { mediaUrl } from '../../utils/media.js'
import { useToast } from '../../composables/useToast.js'

const route = useRoute()
const { smAndDown } = useDisplay()
const { showSuccess, showError, showInfo } = useToast()

const loading = ref(true)
const error = ref('')
const lesson = ref(null)
const activeTab = ref('video')
const reprocessing = ref(false)

const courseId = computed(() => Number(route.params.courseId))
const lessonId = computed(() => Number(route.params.lessonId))

const backLink = computed(() => ({
  name: 'teacher-grade-detail',
  params: { courseId: courseId.value },
}))

const editLink = computed(() => ({
  name: 'teacher-lesson-edit',
  params: { courseId: courseId.value, lessonId: lessonId.value },
}))

const headerSubtitle = computed(() => {
  if (!lesson.value) return ''
  const parts = []
  if (lesson.value.subject_name) parts.push(lesson.value.subject_name)
  if (lesson.value.grade) parts.push(t('teacher.labels.gradeNumber', { grade: lesson.value.grade }))
  if (lesson.value.course_title) parts.push(lesson.value.course_title)
  return parts.join(' · ')
})

const videoSrc = computed(() => mediaUrl(lesson.value?.video_url))
const pdfSrc = computed(() => mediaUrl(lesson.value?.pdf_url))
const audioSrc = computed(() => mediaUrl(lesson.value?.audio_url))

const canReprocess = computed(
  () => lesson.value?.has_pdf && ['error', 'draft', 'processing'].includes(lesson.value?.status),
)

function statusLabel(s, needsReprocessing = false) {
  if (needsReprocessing && s === 'draft') return t('teacher.status.needsReprocess')
  const map = { draft: t('teacher.status.draft'), processing: t('teacher.status.processing'), processed: t('teacher.status.ready'), error: t('teacher.status.error') }
  return map[s] || s
}

function statusColor(s, needsReprocessing = false) {
  if (needsReprocessing && s === 'draft') return 'warning'
  if (s === 'processed') return 'success'
  if (s === 'processing') return 'info'
  if (s === 'error') return 'error'
  return 'warning'
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('ar-SY')
  } catch {
    return '—'
  }
}

function pickDefaultTab() {
  if (!lesson.value) return
  if (lesson.value.has_video) activeTab.value = 'video'
  else if (lesson.value.has_pdf) activeTab.value = 'pdf'
  else if (lesson.value.has_audio) activeTab.value = 'audio'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    lesson.value = await fetchTeacherLessonPreview(courseId.value, lessonId.value)
    pickDefaultTab()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadLesson'))
  } finally {
    loading.value = false
  }
}

async function reprocess() {
  reprocessing.value = true
  try {
    await processCourseLesson(courseId.value, lessonId.value)
    showInfo(t('teacher.status.processingAiRetry'))
    await load()
  } catch (e) {
    showError(getErrorMessage(e, t('teacher.errors.reprocessFailed')))
  } finally {
    reprocessing.value = false
  }
}

watch(() => route.params.lessonId, load)
onMounted(load)
</script>

<style scoped>
.preview-header-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.preview-header-menu {
  min-width: 180px;
}

.preview-panel {
  background: rgb(var(--v-theme-surface)) !important;
  border: 1px solid rgba(var(--v-border-color), 0.14);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
}

.media-frame {
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  max-height: min(60vh, 480px);
}

.media-frame video {
  display: block;
  max-height: min(60vh, 480px);
  object-fit: contain;
}

.pdf-preview-frame {
  width: 100%;
  max-height: min(75vh, 720px);
  overflow: hidden;
  border-radius: 12px;
}

.pdf-iframe {
  display: block;
  width: 100%;
  height: min(75vh, 720px);
  border: 1px solid rgba(var(--v-border-color), 0.14);
  background: #fff;
}

.audio-frame {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-border-color), 0.12);
}

@media (max-width: 959px) {
  .pdf-preview-frame {
    max-height: min(60vh, 520px);
  }

  .pdf-iframe {
    height: min(60vh, 520px);
  }

  .media-frame,
  .media-frame video {
    max-height: min(55vh, 420px);
  }
}

@media (max-width: 599px) {
  .pdf-preview-frame {
    max-height: min(50vh, 360px);
  }

  .pdf-iframe {
    height: min(50vh, 360px);
  }

  .media-frame,
  .media-frame video {
    max-height: min(45vh, 280px);
  }
}
</style>
