<template>
  <ParentPortalShell
    :title="t('parent.lessons.detail.title')"
    :subtitle="t('parent.lessons.detail.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="false"
    load-error=""
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="() => {}"
  >
    <v-btn
      variant="text"
      prepend-icon="mdi-arrow-right"
      class="mb-4"
      :to="ROUTES.PARENT_LESSONS"
    >
      {{ t('parent.lessons.detail.back') }}
    </v-btn>

    <LoadingState v-if="loading" variant="inline" :label="t('parent.lessons.detail.loading')" />

    <v-alert v-else-if="error" type="error" variant="tonal">{{ error }}</v-alert>

    <template v-else-if="detail">
      <v-card class="glass-card glass-card--elevated pa-5 mb-5" variant="flat">
        <div class="d-flex align-start justify-space-between flex-wrap gap-3 mb-4">
          <div>
            <p class="text-caption text-medium-emphasis mb-1">{{ detail.course_title }}</p>
            <h2 class="text-h5 font-weight-bold mb-2">{{ detail.lesson_title }}</h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              <v-icon size="16" class="me-1">mdi-account-tie</v-icon>
              {{ detail.teacher_name }}
            </p>
          </div>
          <v-chip
            :color="detail.is_verified ? 'success' : detail.completion_status_code === 'in_progress' ? 'warning' : 'default'"
            variant="flat"
            size="large"
          >
            {{ detail.verification_status_label }}
          </v-chip>
        </div>

        <v-row dense>
          <v-col cols="6" sm="3">
            <div class="meta-pill pa-3 rounded-lg">
              <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.lessons.detail.completionStatus') }}</p>
              <p class="text-body-2 font-weight-bold mb-0">{{ detail.completion_status }}</p>
            </div>
          </v-col>
          <v-col v-if="detail.completed_at" cols="6" sm="3">
            <div class="meta-pill pa-3 rounded-lg">
              <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.lessons.detail.completionDate') }}</p>
              <p class="text-body-2 font-weight-bold mb-0">{{ formatDate(detail.completed_at) }}</p>
            </div>
          </v-col>
          <v-col v-if="detail.started_at" cols="6" sm="3">
            <div class="meta-pill pa-3 rounded-lg">
              <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.lessons.detail.startDate') }}</p>
              <p class="text-body-2 font-weight-bold mb-0">{{ formatDate(detail.started_at) }}</p>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <v-row class="mb-5">
        <v-col cols="12" md="4">
          <v-card class="glass-card pa-4 h-100" variant="flat">
            <div class="d-flex align-center gap-2 mb-3">
              <v-icon color="primary">mdi-play-circle</v-icon>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.lessons.detail.video') }}</h3>
            </div>
            <div class="text-h4 font-weight-bold eduspark-gradient-text mb-2">
              {{ detail.video_progress_percent }}%
            </div>
            <v-progress-linear :model-value="detail.video_progress_percent" color="primary" rounded height="8" />
            <p v-if="detail.video_last_watched_at" class="text-caption text-medium-emphasis mt-3 mb-0">
              {{ t('parent.lessons.detail.lastWatched', { date: formatDateTime(detail.video_last_watched_at) }) }}
            </p>
            <p v-else class="text-caption text-medium-emphasis mt-3 mb-0">{{ t('parent.lessons.detail.noWatchYet') }}</p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="glass-card pa-4 h-100" variant="flat">
            <div class="d-flex align-center gap-2 mb-3">
              <v-icon color="secondary">mdi-file-document-outline</v-icon>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.common.pdf') }}</h3>
            </div>
            <div class="text-h4 font-weight-bold mb-2">
              <template v-if="detail.pdf_total_pages">
                {{ t('parent.lessons.detail.pdfPages', { n: detail.pdf_pages_viewed ?? 0, total: detail.pdf_total_pages }) }}
              </template>
              <template v-else>{{ detail.pdf_progress_percent }}%</template>
            </div>
            <v-progress-linear :model-value="detail.pdf_progress_percent" color="secondary" rounded height="8" />
            <p class="text-caption text-medium-emphasis mt-3 mb-0">
              {{ t('parent.lessons.detail.pdfStatus', {
                percent: detail.pdf_progress_percent,
                status: detail.pdf_opened ? t('parent.lessons.detail.fileOpened') : t('parent.lessons.detail.fileNotOpened'),
              }) }}
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="glass-card pa-4 h-100" variant="flat">
            <div class="d-flex align-center gap-2 mb-3">
              <v-icon color="warning">mdi-clipboard-check-outline</v-icon>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.lessons.detail.quiz') }}</h3>
            </div>
            <div class="text-h4 font-weight-bold mb-2">{{ detail.quiz_score_percent }}%</div>
            <p class="text-body-2 mb-1">{{ t('parent.lessons.detail.attemptCount', { n: detail.quiz_attempt_count }) }}</p>
            <p v-if="detail.quiz_last_attempt_at" class="text-caption text-medium-emphasis mb-0">
              {{ t('parent.lessons.detail.lastAttempt', { date: formatDateTime(detail.quiz_last_attempt_at) }) }}
            </p>
            <p v-else class="text-caption text-medium-emphasis mb-0">{{ t('parent.lessons.detail.noAttempts') }}</p>
          </v-card>
        </v-col>
      </v-row>

      <v-card class="glass-card pa-4 pa-md-5 mb-5" variant="flat">
        <div class="d-flex align-center gap-2 mb-4">
          <v-icon :color="detail.is_verified ? 'success' : 'warning'">mdi-shield-check</v-icon>
          <h3 class="text-subtitle-1 font-weight-bold mb-0">
            {{ detail.is_verified ? t('parent.lessons.detail.verifiedCompletion') : t('parent.lessons.detail.incomplete') }}
          </h3>
        </div>

        <v-list v-if="detail.checklist?.length" density="compact" class="bg-transparent mb-4">
          <v-list-item v-for="item in detail.checklist" :key="item.key">
            <template #prepend>
              <v-icon :color="item.met ? 'success' : 'error'" size="20">
                {{ item.met ? 'mdi-check-circle' : 'mdi-close-circle-outline' }}
              </v-icon>
            </template>
            <v-list-item-title class="text-body-2">{{ item.label }}</v-list-item-title>
          </v-list-item>
        </v-list>

        <v-alert
          v-if="detail.missing_requirements?.length && !detail.is_verified"
          type="warning"
          variant="tonal"
          density="compact"
          class="rounded-lg"
        >
          <p class="text-subtitle-2 font-weight-bold mb-2">{{ t('parent.lessons.detail.missingRequirements') }}</p>
          <ul class="mb-0 ps-4">
            <li v-for="(req, idx) in detail.missing_requirements" :key="idx">{{ req }}</li>
          </ul>
        </v-alert>
      </v-card>

      <v-card v-if="detail.timeline?.length" class="glass-card pa-4 pa-md-5" variant="flat">
        <div class="d-flex align-center gap-2 mb-4">
          <v-icon color="info">mdi-timeline-clock-outline</v-icon>
          <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.lessons.detail.activityLog') }}</h3>
        </div>
        <v-timeline side="end" density="compact" truncate-line="both">
          <v-timeline-item
            v-for="(event, idx) in detail.timeline"
            :key="idx"
            :dot-color="idx === detail.timeline.length - 1 ? 'success' : 'primary'"
            size="small"
          >
            <p class="text-caption text-medium-emphasis mb-0">{{ event.date }}</p>
            <p class="text-body-2 font-weight-medium mb-0">{{ event.label }}</p>
          </v-timeline-item>
        </v-timeline>
      </v-card>
    </template>
  </ParentPortalShell>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import { fetchParentLessonDetail } from '../../api/parent.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'

const { t, locale } = useI18n()
const route = useRoute()
const lessonId = computed(() => Number(route.params.lessonId))

const shell = useParentShell()
const {
  students,
  selectedStudentId,
  studentContext,
  hasStudents,
  loadingStudents,
  studentsError,
  linking,
  linkError,
  linkSuccess,
  selectStudent,
  linkStudent,
} = shell

const loading = ref(false)
const error = ref('')
const detail = ref(null)

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString(dateLocale(), { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return iso
  }
}

function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString(dateLocale(), {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

async function load() {
  if (!lessonId.value || selectedStudentId.value == null) return
  loading.value = true
  error.value = ''
  detail.value = null
  try {
    detail.value = await fetchParentLessonDetail(lessonId.value, selectedStudentId.value)
  } catch (e) {
    error.value = getErrorMessage(e, t('parent.errors.loadLessonDetail'))
  } finally {
    loading.value = false
  }
}

useParentPageLoad(shell, load, 'lesson-detail')

watch(lessonId, () => load())
</script>

<style scoped>
.meta-pill {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  height: 100%;
}
</style>
