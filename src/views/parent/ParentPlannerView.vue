<template>
  <ParentPortalShell
    :title="t('parent.planner.title')"
    :subtitle="t('parent.planner.subtitle')"
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
    <ParentPlannerCommitmentSection :planner="planner" />

    <v-divider class="my-8" />

    <h2 class="text-h6 font-weight-bold mb-4">{{ t('parent.planner.dailyRoutine') }}</h2>
    <ParentRoutineCommitmentSection :routine="routine" />
  </ParentPortalShell>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentPlannerCommitmentSection from '../../components/parent/ParentPlannerCommitmentSection.vue'
import ParentRoutineCommitmentSection from '../../components/parent/ParentRoutineCommitmentSection.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentMonitor } from '../../composables/useParentMonitor.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'
import { fetchParentRoutineApi } from '../../api/parent.js'

const { t } = useI18n()

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

const { loading, loadError, planner, load } = useParentMonitor(shell.selectedStudentId)

const routine = ref(null)

async function loadPage() {
  await Promise.all([
    load(),
    fetchParentRoutineApi(shell.selectedStudentId.value).then((data) => {
      routine.value = data
    }),
  ])
}

useParentPageLoad(shell, loadPage, 'planner')
</script>
