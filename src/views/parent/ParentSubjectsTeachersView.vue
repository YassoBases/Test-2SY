<template>
  <ParentPortalShell
    :title="t('parent.subjectsTeachers.title')"
    :subtitle="t('parent.subjectsTeachers.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="subjectsLoading"
    :load-error="subjectsLoadError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="subjectsLoadError = ''"
  >
    <v-alert
      v-if="chatError"
      type="error"
      variant="tonal"
      class="mb-4 rounded-lg"
      closable
      @click:close="chatError = ''"
    >
      {{ chatError }}
    </v-alert>

    <ParentSubjectsTeachersSection
      :data="subjectsData"
      :contacting-course-id="contactingCourseId"
      @view-profile="onViewProfile"
      @contact="onContact"
    />

    <StudentTeacherProfileDialog
      v-model="profileOpen"
      :profile="teacherProfile"
      :loading="profileLoading"
    />

    <v-alert
      v-if="profileOpen && profileError"
      type="error"
      variant="tonal"
      class="mt-4 rounded-lg"
      closable
      @click:close="profileError = ''"
    >
      {{ profileError }}
    </v-alert>
  </ParentPortalShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentSubjectsTeachersSection from '../../components/parent/ParentSubjectsTeachersSection.vue'
import StudentTeacherProfileDialog from '../../components/student/StudentTeacherProfileDialog.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentSubjectsTeachers } from '../../composables/useParentSubjectsTeachers.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'
import { openParentTeacherChat } from '../../api/parentMessaging.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()
const router = useRouter()
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

const subjectsTeachers = useParentSubjectsTeachers(shell.selectedStudentId)
const {
  loading: subjectsLoading,
  loadError: subjectsLoadError,
  profileError,
  data: subjectsData,
  profileLoading,
  teacherProfile,
  loadTeacherProfile,
  load: loadSubjects,
} = subjectsTeachers

useParentPageLoad(shell, loadSubjects, 'subjects-teachers')

const profileOpen = ref(false)
const contactingCourseId = ref(null)
const chatError = ref('')

async function onViewProfile(item) {
  profileOpen.value = true
  profileError.value = ''
  await loadTeacherProfile(item.course_id)
}

async function onContact(item) {
  if (!item.enrolled || contactingCourseId.value != null) return
  contactingCourseId.value = item.course_id
  chatError.value = ''
  try {
    const result = await openParentTeacherChat(item.teacher_user_id, {
      studentId: subjectsData.value?.student_id ?? selectedStudentId.value,
      courseId: item.course_id,
    })
    await router.push({
      path: ROUTES.PARENT_MESSAGES,
      query: { thread: String(result.thread_id) },
    })
  } catch (err) {
    chatError.value = getErrorMessage(err, t('parent.subjectsTeachers.errors.openChat'))
  } finally {
    contactingCourseId.value = null
  }
}
</script>
