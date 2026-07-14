<template>
  <div class="course-view slide-up-enter-active" dir="rtl">
    <LoadingState v-if="loading" variant="cards" :count="2" class="mb-6" />

    <template v-else-if="course">
      <v-card v-if="!course.unlocked" class="locked-screen glass-card text-center" variant="flat">
        <div class="pa-6 pa-md-8">
        <TeacherAvatar
          :name="course.teacher_name"
          :image-url="course.teacher_image_url || course.avatar_url"
          :size="88"
          class="mb-4"
        />
        <p class="text-caption text-medium-emphasis mb-1">{{ course.subject_name }}</p>
        <h2 class="text-h5 font-weight-bold mb-2">{{ t('student.course.locked.withTeacher', { teacher: course.teacher_name }) }}</h2>
        <v-icon size="48" color="warning" class="my-4">mdi-lock-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-2">{{ t('student.course.locked.title') }}</h3>
        <p class="text-body-2 text-medium-emphasis mb-6 mx-auto" style="max-width: 320px">
          {{ t('student.course.locked.subscribePrompt', {
            count: course.lesson_count,
            countLabel: course.lesson_count === 1 ? t('student.common.lesson') : t('student.common.lessons'),
            teacher: course.teacher_name,
          }) }}
        </p>
        <v-btn size="x-large" rounded="lg" class="btn-glow" :to="ROUTES.STUDENT_SUBSCRIPTIONS">
          {{ t('student.course.locked.subscribeCta') }}
        </v-btn>
        <v-btn variant="text" class="mt-3" :to="ROUTES.STUDENT_COURSES">{{ t('student.course.backToCourses') }}</v-btn>
        </div>
      </v-card>

      <div v-else class="course-layout">
        <v-tabs v-model="courseTab" class="course-tabs" color="primary" grow>
          <v-tab value="lessons">
            <v-icon start>mdi-play-circle-outline</v-icon>
            {{ t('student.course.tabs.lessons') }}
          </v-tab>
          <v-tab value="quizzes">
            <v-icon start>mdi-clipboard-text</v-icon>
            {{ t('student.course.tabs.quizzes') }}
            <v-chip v-if="manualQuizzes.length" size="x-small" class="ms-2" color="secondary">
              {{ manualQuizzes.length }}
            </v-chip>
          </v-tab>
        </v-tabs>

        <div v-if="courseTab === 'lessons'" class="course-experience">
          <CourseHero
            :subject-name="course.subject_name"
            :teacher-name="course.teacher_name"
            :teacher-image-url="course.teacher_image_url || course.avatar_url"
            :progress-percent="course.progress_percent"
            :completed-lesson-count="course.completed_lesson_count"
            :lesson-count="course.lesson_count"
            :can-contact="course.unlocked"
            :has-linked-parent="course.has_linked_parent"
            :messaging="openingChat"
            @message-teacher="onMessageTeacher"
            @view-profile="openTeacherProfile"
          />
          <CourseCurrentLesson
            :lesson="currentJourneyLesson"
            :teacher-name="course.teacher_name"
            :subject-name="course.subject_name"
            :lesson-count="course.lesson_count"
            :completed-lesson-count="course.completed_lesson_count"
            :progress-percent="course.progress_percent"
            :all-completed="allLessonsCompleted"
            @continue="continueLearning"
          />
          <CourseLessonJourney
            :lessons="journeyLessons"
            @select="selectLesson"
          />
        </div>

        <v-card v-else class="glass-card course-quizzes-wrap pa-0" variant="flat">
          <CourseQuizzesPanel
            :course-id="course.id"
            :unlocked="course.unlocked"
          />
        </v-card>
      </div>
    </template>

    <v-alert v-else-if="error" type="error" variant="tonal" class="ma-4">{{ error }}</v-alert>

    <StudentTeacherProfileDialog
      v-model="showTeacherProfile"
      :profile="teacherProfile"
      :loading="loadingTeacherProfile"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import LoadingState from '../../components/common/LoadingState.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import CourseQuizzesPanel from '../../components/student/CourseQuizzesPanel.vue'
import CourseHero from '../../components/student/course/CourseHero.vue'
import CourseCurrentLesson from '../../components/student/course/CourseCurrentLesson.vue'
import CourseLessonJourney from '../../components/student/course/CourseLessonJourney.vue'
import StudentTeacherProfileDialog from '../../components/student/StudentTeacherProfileDialog.vue'
import {
  deriveLessonJourneyState,
  findCurrentLesson,
  findNextLesson,
} from '../../composables/useCourseLessonJourney.js'
import {
  fetchCourseTeacherProfile,
  fetchStudentCourse,
  openCourseTeacherChat,
} from '../../api/studentCourses.js'
import { fetchStudentManualQuizzes } from '../../api/manualQuizzes.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import '../../assets/styles/course-experience.css'
import '../../assets/styles/ui-6.4-course-messages.css'
import '../../assets/styles/ui-course-7.1.css'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const course = ref(null)
const loading = ref(true)
const error = ref('')
const manualQuizzes = ref([])
const courseTab = ref('lessons')
const openingChat = ref(false)
const showTeacherProfile = ref(false)
const teacherProfile = ref(null)
const loadingTeacherProfile = ref(false)

const journeyLessons = computed(() =>
  deriveLessonJourneyState(course.value?.lessons || [], course.value?.unlocked !== false),
)

const nextLesson = computed(() => findNextLesson(course.value?.lessons || []))

const currentJourneyLesson = computed(() => {
  const lessons = journeyLessons.value
  if (!lessons.length) return null
  const current = lessons.find((l) => l.journeyState === 'current')
  if (current) return current
  const raw = findCurrentLesson(course.value?.lessons || [])
  if (!raw) return null
  return lessons.find((l) => l.id === raw.id) || { ...raw, journeyIndex: lessons.length, journeyState: 'completed' }
})

const allLessonsCompleted = computed(() => {
  const lessons = course.value?.lessons || []
  return lessons.length > 0 && lessons.every((l) => l.completed)
})

function selectLesson(lesson) {
  router.push({
    path: `/student/lesson/${lesson.id}`,
    query: course.value?.id ? { courseId: course.value.id } : {},
  })
}

function continueLearning() {
  if (!nextLesson.value) return
  selectLesson(nextLesson.value)
}

async function onMessageTeacher({ includeParent }) {
  if (!course.value?.id || !course.value.unlocked) return
  openingChat.value = true
  error.value = ''
  try {
    const result = await openCourseTeacherChat(course.value.id, { includeParent })
    const threadId = result.thread_id || course.value.existing_message_thread_id
    if (threadId) {
      router.push({ path: ROUTES.STUDENT_MESSAGES, query: { thread: threadId } })
    } else {
      router.push(ROUTES.STUDENT_MESSAGES)
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('student.course.errors.openChat'))
  } finally {
    openingChat.value = false
  }
}

async function openTeacherProfile() {
  if (!course.value?.id) return
  showTeacherProfile.value = true
  loadingTeacherProfile.value = true
  teacherProfile.value = null
  try {
    teacherProfile.value = await fetchCourseTeacherProfile(course.value.id)
  } catch (e) {
    error.value = getErrorMessage(e, t('student.course.errors.loadTeacherProfile'))
    showTeacherProfile.value = false
  } finally {
    loadingTeacherProfile.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    course.value = await fetchStudentCourse(route.params.id)
    if (course.value?.unlocked) {
      try {
        manualQuizzes.value = await fetchStudentManualQuizzes(Number(route.params.id))
      } catch {
        manualQuizzes.value = []
      }
    } else {
      manualQuizzes.value = []
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('student.course.errors.loadCourse'))
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, load)
watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'quizzes') courseTab.value = 'quizzes'
  },
  { immediate: true },
)
onMounted(load)
</script>

<style scoped>
.course-view {
  min-height: calc(100dvh - 80px);
}

.course-layout {
  display: flex;
  flex-direction: column;
  min-height: calc(100dvh - 100px);
}

.course-tabs {
  flex-shrink: 0;
}

.course-quizzes-wrap {
  flex: 1;
  overflow: hidden;
}
</style>
