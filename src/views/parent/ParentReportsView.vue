<template>
  <ParentPortalShell
    :title="t('parent.reports.title')"
    :subtitle="t('parent.reports.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="reportsLoading"
    :load-error="visibleLoadError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="clearReportsLoadError"
  >
    <ParentHistoricalReportsSection
      :report="report"
      :loading="reportsLoading"
      :exporting="reportsExporting"
      :load-error="visibleLoadError"
      :export-error="visibleExportError"
      :period="reportsPeriod"
      :custom-start="reportsCustomStart"
      :custom-end="reportsCustomEnd"
      @period-change="onPeriodChange"
      @export="exportReport"
      @apply-custom="loadReports"
      @retry="retryReports"
      @clear-export-error="clearReportsExportError"
      @update:custom-start="reportsCustomStart = $event"
      @update:custom-end="reportsCustomEnd = $event"
    />
  </ParentPortalShell>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentHistoricalReportsSection from '../../components/parent/portal/ParentHistoricalReportsSection.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentHistoricalReports } from '../../composables/useParentHistoricalReports.js'
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

const reports = useParentHistoricalReports(shell.selectedStudentId)

const {
  report,
  loading: reportsLoading,
  exporting: reportsExporting,
  loadError: reportsLoadError,
  exportError: reportsExportError,
  period: reportsPeriod,
  customStart: reportsCustomStart,
  customEnd: reportsCustomEnd,
  setPeriod,
  load: loadReports,
  retryLoad,
  exportReport,
  resetPeriodAndLoad,
  clearLoadError,
  clearExportError,
} = reports

const visibleLoadError = computed(() => (report.value ? '' : reportsLoadError.value))
const visibleExportError = computed(() => reportsExportError.value)

useParentPageLoad(shell, resetPeriodAndLoad, 'reports', { beforeLoad: clearLoadError })

function clearReportsLoadError() {
  clearLoadError('ui:dismiss-load')
}

function clearReportsExportError() {
  clearExportError('ui:dismiss-export')
}

function retryReports() {
  retryLoad()
}

function onPeriodChange(value) {
  setPeriod(value)
}
</script>
