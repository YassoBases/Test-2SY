<template>
  <ParentPortalShell
    :title="t('parent.attendance.title')"
    :subtitle="t('parent.attendance.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="loading || attendanceAnalyticsLoading"
    :load-error="loadError || attendanceAnalyticsError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="clearErrors"
  >
    <ParentStudyTimeAveragesSection
      v-if="attendanceAnalyticsData?.overview?.averages"
      :averages="attendanceAnalyticsData.overview.averages"
      class="mb-2"
    />

    <ParentStudyTimeAnalyticsSection
      :analytics="attendanceAnalyticsData"
      :loading="attendanceAnalyticsLoading"
      :error="attendanceAnalyticsError"
      :week-offset="weekOffset"
      :month-offset="monthOffset"
      @week-offset="setWeekOffset"
      @month-offset="setMonthOffset"
    />

    <ParentAttendanceSection
      v-if="attendance && Object.keys(attendance).length"
      :summary="attendance"
      class="mt-6"
    />
  </ParentPortalShell>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentStudyTimeAveragesSection from '../../components/parent/portal/ParentStudyTimeAveragesSection.vue'
import ParentStudyTimeAnalyticsSection from '../../components/parent/ParentStudyTimeAnalyticsSection.vue'
import ParentAttendanceSection from '../../components/parent/ParentAttendanceSection.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentMonitor } from '../../composables/useParentMonitor.js'
import { useParentAttendanceAnalytics } from '../../composables/useParentAttendanceAnalytics.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'

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

const { loading, loadError, attendance, load: loadMonitor } = useParentMonitor(shell.selectedStudentId)

const attendanceAnalytics = useParentAttendanceAnalytics(shell.selectedStudentId)
const {
  analytics: attendanceAnalyticsData,
  loading: attendanceAnalyticsLoading,
  error: attendanceAnalyticsError,
  weekOffset,
  monthOffset,
  setWeekOffset,
  setMonthOffset,
  resetOffsetsAndLoad,
} = attendanceAnalytics

async function loadAttendancePage() {
  await Promise.all([loadMonitor(), resetOffsetsAndLoad()])
}

useParentPageLoad(shell, loadAttendancePage, 'attendance')

function clearErrors() {
  loadError.value = ''
  attendanceAnalyticsError.value = ''
}
</script>
