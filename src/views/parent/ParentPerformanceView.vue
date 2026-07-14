<template>
  <ParentPortalShell
    :title="t('parent.performance.title')"
    :subtitle="t('parent.performance.subtitle')"
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
    <ParentAcademicIntelligenceSection :data="academicIntelligence" class="mb-6" />

    <v-row class="mb-6">
      <v-col cols="12" lg="7">
        <ParentQuizSection :quiz="quiz" />
      </v-col>
      <v-col cols="12" lg="5">
        <ParentCourseProgressSection :items="courseProgress" />
      </v-col>
    </v-row>

    <v-card v-if="gamification" class="glass-card pa-5" variant="flat">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="secondary">mdi-trophy-outline</v-icon>
        <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('parent.performance.gamification') }}</h3>
      </div>
      <GamificationPanel :profile="gamification" read-only />
    </v-card>
  </ParentPortalShell>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentAcademicIntelligenceSection from '../../components/parent/ParentAcademicIntelligenceSection.vue'
import ParentQuizSection from '../../components/parent/ParentQuizSection.vue'
import ParentCourseProgressSection from '../../components/parent/ParentCourseProgressSection.vue'
import GamificationPanel from '../../components/gamification/GamificationPanel.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentMonitor } from '../../composables/useParentMonitor.js'
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

const {
  loading,
  loadError,
  academicIntelligence,
  quiz,
  courseProgress,
  gamification,
  load,
} = useParentMonitor(shell.selectedStudentId)

useParentPageLoad(shell, load, 'performance')
</script>
