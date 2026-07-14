<template>
  <ParentPortalShell
    :title="t('parent.lessons.title')"
    :subtitle="t('parent.lessons.subtitle')"
    max-width="1100px"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="loading"
    :load-error="loadError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="loadError = ''"
  >
    <ParentLessonProgressSection
      v-if="lessonProgress?.summary"
      :summary="lessonProgress.summary"
      :courses="lessonProgress.courses || []"
      @open-lesson="openLessonDetail"
    />

    <v-alert v-else type="info" variant="tonal" class="rounded-lg">
      {{ t('parent.lessons.noData') }}
    </v-alert>
  </ParentPortalShell>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentLessonProgressSection from '../../components/parent/ParentLessonProgressSection.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentMonitor } from '../../composables/useParentMonitor.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'

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

const { loading, loadError, lessonProgress, load } = useParentMonitor(shell.selectedStudentId)

useParentPageLoad(shell, load, 'lessons')

function openLessonDetail(lessonId) {
  router.push({
    name: 'parent-lesson-detail',
    params: { lessonId: String(lessonId) },
  })
}
</script>
