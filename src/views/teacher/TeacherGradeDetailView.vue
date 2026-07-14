<template>
  <div class="slide-up-enter-active teacher-class-detail" dir="rtl">
    <div v-show="!showAddLesson">
    <PageHeader
      :eyebrow="$t('teacher.grades.detailEyebrow')"
      :title="headerTitle"
      :subtitle="headerSubtitle"
    >
      <template #actions>
        <v-btn variant="tonal" rounded="lg" class="me-2" @click="showEditCourse = true">
          <v-icon start>mdi-pencil-outline</v-icon>
          {{ $t('teacher.actions.editCourse') }}
        </v-btn>
        <v-btn class="btn-glow" rounded="lg" @click="showAddLesson = true">
          <v-icon start>mdi-upload</v-icon>
          {{ $t('teacher.actions.addLesson') }}
        </v-btn>
      </template>
    </PageHeader>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-5 rounded-lg">{{ error }}</v-alert>

    <v-row v-if="loading" class="mb-6">
      <v-col v-for="i in 3" :key="i" cols="12" md="6" lg="4">
        <v-skeleton-loader type="card" class="glass-card rounded-lg" />
      </v-col>
    </v-row>

    <template v-else-if="course">
      <v-card v-if="course.banner_url || course.thumbnail_url" class="glass-card mb-6 overflow-hidden" variant="flat">
        <v-img
          :src="mediaUrl(course.banner_url || course.thumbnail_url)"
          height="160"
          cover
          gradient="to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.65)"
        >
          <div class="pa-6 d-flex flex-column justify-end h-100">
            <v-chip size="small" :color="course.is_published ? 'success' : 'warning'" variant="flat" class="align-self-start mb-2">
              {{ course.is_published ? $t('teacher.status.published') : $t('teacher.status.draft') }}
            </v-chip>
            <div class="text-h6 font-weight-bold">{{ course.subject_name }}</div>
            <div
              v-if="course.title && course.title !== course.subject_name"
              class="text-body-2 text-medium-emphasis mt-1"
            >
              {{ course.title }}
            </div>
            <div v-if="course.description" class="text-body-2 text-medium-emphasis mt-1">{{ course.description }}</div>
            <div class="text-caption mt-2">{{ formatPrice(course.price) }}</div>
          </div>
        </v-img>
      </v-card>

      <v-row class="mb-6">
        <v-col cols="6" md="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-success">{{ course.analytics.active_subscribers }}</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.grades.activeStudents') }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-warning">{{ course.analytics.expiring_soon }}</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.status.expiringSoon') }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-error">{{ course.analytics.expired_subscribers }}</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.status.expired') }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-secondary">{{ course.analytics.subscribed_students }}</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.grades.totalPaid') }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mb-6">
        <v-col cols="6" md="4">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold">{{ course.analytics.lesson_count }}</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.grades.lessonCount') }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" md="4">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-warning">{{ course.analytics.completion_percent }}%</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.grades.lessonCompletionRate') }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold">{{ course.analytics.avg_quiz_percent }}%</div>
            <div class="text-caption text-medium-emphasis">{{ $t('teacher.grades.avgQuizResults') }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="teacher-class-detail__workspace" dense>
        <v-col cols="12" lg="6">
          <section class="class-workspace-panel">
            <TeacherClassWorkspaceToolbar
              v-model:search="lessonSearch"
              :count="course.lessons.length"
              :show-filter-shell="true"
            >
              <template #actions>
                <v-btn class="btn-glow" rounded="lg" @click="showAddLesson = true">
                  <v-icon start>mdi-plus</v-icon>
                  {{ $t('teacher.actions.addLesson') }}
                </v-btn>
              </template>
            </TeacherClassWorkspaceToolbar>

            <TeacherLessonWorkspaceEmpty
              v-if="!course.lessons.length"
              @add="showAddLesson = true"
            />

            <div v-else-if="!filteredLessons.length" class="class-workspace-empty">
              {{ $t('teacher.grades.noLessonMatch') }}
            </div>

            <div v-else class="class-workspace-list">
              <TeacherLessonPremiumCard
                v-for="l in filteredLessons"
                :key="l.id"
                :lesson="l"
                :active-students="course.analytics.active_subscribers"
                :preview-to="previewLink(l.id)"
                :edit-to="editLink(l.id)"
                :show-ai="canReprocess(l)"
                :ai-loading="processingId === l.id"
                @ai="processLesson(l.id)"
              />
            </div>
          </section>
        </v-col>

        <v-col cols="12" lg="6">
          <TeacherStudentSummaryPanel
            v-if="course"
            :analytics="course.analytics"
            :students="course.students"
            :grade="course.grade"
            :subject-id="course.subject_id"
          />
        </v-col>
      </v-row>
    </template>
    </div>

    <AddLessonDialog
      v-if="courseId"
      v-model="showAddLesson"
      :course-id="courseId"
      @uploaded="load"
    />

    <EditCourseDialog
      v-model="showEditCourse"
      :course="course"
      @saved="load"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import AddLessonDialog from '../../components/teacher/AddLessonDialog.vue'
import EditCourseDialog from '../../components/teacher/EditCourseDialog.vue'
import TeacherLessonWorkspaceEmpty from '../../components/teacher/lessons/TeacherLessonWorkspaceEmpty.vue'
import TeacherLessonPremiumCard from '../../components/teacher/lessons/TeacherLessonPremiumCard.vue'
import TeacherClassWorkspaceToolbar from '../../components/teacher/lessons/TeacherClassWorkspaceToolbar.vue'
import TeacherStudentSummaryPanel from '../../components/teacher/lessons/TeacherStudentSummaryPanel.vue'
import { fetchTeacherCourseDetail } from '../../api/teacherDashboard.js'
import { processCourseLesson, regenerateCourseLessonQuiz } from '../../api/teacherCourses.js'
import { getApiBaseUrl, getErrorMessage } from '../../api/client.js'
import { canReprocessLesson } from '../../utils/lessonWorkspaceDisplay.js'
import '../../assets/styles/teacher-class-detail.css'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const course = ref(null)
const showAddLesson = ref(false)
const showEditCourse = ref(false)
const processingId = ref(null)
const quizId = ref(null)
const lessonSearch = ref('')

const courseId = computed(() => route.params.courseId)

const headerTitle = computed(() => {
  if (!course.value) return '...'
  return t('teacher.labels.subjectGradeDash', { subject: course.value.subject_name, grade: course.value.grade })
})
const headerSubtitle = computed(() => {
  if (!course.value) return ''
  return course.value.description || t('teacher.grades.subjectCourseDesc', { subject: course.value.subject_name, grade: course.value.grade })
})

const filteredLessons = computed(() => {
  const list = course.value?.lessons || []
  const q = lessonSearch.value.trim().toLowerCase()
  if (!q) return list
  return list.filter((l) => String(l.title || '').toLowerCase().includes(q))
})

function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = getApiBaseUrl().replace(/\/api$/, '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

function formatPrice(n) {
  const v = Number(n)
  if (!v) return t('teacher.labels.free')
  return t('teacher.labels.currencySyp', { amount: v.toLocaleString('ar-SY') })
}

function canReprocess(lesson) {
  return canReprocessLesson(lesson)
}

function previewLink(lessonId) {
  return {
    name: 'teacher-lesson-preview',
    params: { courseId: courseId.value, lessonId },
  }
}

function editLink(lessonId) {
  return {
    name: 'teacher-lesson-edit',
    params: { courseId: courseId.value, lessonId },
  }
}

async function processLesson(lessonId) {
  processingId.value = lessonId
  error.value = ''
  try {
    await processCourseLesson(Number(courseId.value), lessonId)
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.processingFailed'))
  } finally {
    processingId.value = null
  }
}

async function generateQuiz(lessonId) {
  quizId.value = lessonId
  error.value = ''
  try {
    await regenerateCourseLessonQuiz(Number(courseId.value), lessonId)
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.createQuiz'))
  } finally {
    quizId.value = null
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    course.value = await fetchTeacherCourseDetail(route.params.courseId)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadDetails'))
  } finally {
    loading.value = false
  }
}

watch(() => route.params.courseId, load)
onMounted(load)
</script>
