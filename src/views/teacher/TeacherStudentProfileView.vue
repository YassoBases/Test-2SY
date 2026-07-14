<template>
  <div class="slide-up-enter-active" dir="rtl">
    <PageHeader
      :eyebrow="$t('teacher.students.profileEyebrow')"
      :title="profile?.info?.full_name || '—'"
      :subtitle="$t('teacher.students.profileSubtitle')"
    >
      <template #actions>
        <v-btn variant="tonal" rounded="lg" :to="{ name: 'teacher-students' }">
          <v-icon start>mdi-arrow-right</v-icon>
          {{ $t('teacher.actions.backToStudents') }}
        </v-btn>
      </template>
    </PageHeader>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <v-row v-if="loading">
      <v-col v-for="i in 4" :key="i" cols="12" md="3">
        <v-skeleton-loader type="card" class="glass-card rounded-lg" />
      </v-col>
    </v-row>

    <template v-else-if="profile">
      <v-alert
        v-if="profile.analytics_scope_label"
        type="info"
        variant="tonal"
        density="compact"
        class="mb-4 rounded-lg"
      >
        {{ $t('teacher.students.statsScope') }} {{ profile.analytics_scope_label }}
      </v-alert>

      <!-- Analytics summary cards -->
      <v-row class="mb-6">
        <v-col v-for="card in summaryCards" :key="card.id" cols="6" md="4" lg="2">
          <v-card class="glass-card kpi-card pa-4 text-center h-100" variant="flat">
            <v-icon :icon="card.icon" :color="card.color" size="28" class="mb-2" />
            <div class="text-h6 font-weight-bold">{{ card.value }}</div>
            <div class="text-caption text-medium-emphasis">{{ card.label }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <!-- Student info -->
        <v-col cols="12" lg="4">
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <div class="d-flex align-center gap-4 mb-4">
              <TeacherAvatar :name="profile.info.full_name" :size="72" />
              <div>
                <div class="text-h6 font-weight-bold">{{ profile.info.full_name }}</div>
                <div class="text-caption text-medium-emphasis">{{ profile.info.email }}</div>
                <v-chip
                  size="x-small"
                  :color="profile.info.account_status === 'active' ? 'success' : 'warning'"
                  variant="tonal"
                  class="mt-1"
                >
                  {{ profile.info.account_status === 'active' ? $t('teacher.status.active') : $t('teacher.status.expired') }}
                </v-chip>
              </div>
            </div>
            <v-list density="compact" class="bg-transparent pa-0">
              <v-list-item prepend-icon="mdi-school-outline" :title="$t('teacher.labels.grade')">
                <template #subtitle>{{ profile.info.grade ? $t('teacher.labels.gradeNumber', { grade: profile.info.grade }) : '—' }}</template>
              </v-list-item>
              <v-list-item prepend-icon="mdi-calendar-plus" :title="$t('teacher.labels.enrolledAt')">
                <template #subtitle>{{ formatDate(profile.info.registration_date) }}</template>
              </v-list-item>
              <v-list-item prepend-icon="mdi-login" :title="$t('teacher.labels.lastLogin')">
                <template #subtitle>{{ formatDate(profile.info.last_login_at) }}</template>
              </v-list-item>
            </v-list>
          </v-card>

          <TeacherStudentParentContactSection
            :student-id="studentId"
            :parents="profile.linked_parents || []"
          />
        </v-col>

        <!-- Learning + Quiz -->
        <v-col cols="12" lg="8">
          <TeacherStudentInsightPanel :insight="profile.teacher_insight" />

          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-h6 font-weight-bold mb-4">{{ $t('teacher.students.learningOverview') }}</h3>
            <v-row dense class="mb-4">
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-primary">{{ profile.learning.active_courses }}</div>
                <div class="text-caption">{{ $t('teacher.students.activeSubjects') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-success">{{ profile.learning.completed_courses }}</div>
                <div class="text-caption">{{ $t('teacher.students.completedSubjects') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold">{{ profile.learning.lessons_completed }}</div>
                <div class="text-caption">{{ $t('teacher.students.completedLessons') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-warning">{{ profile.learning.lessons_remaining }}</div>
                <div class="text-caption">{{ $t('teacher.students.remainingLessons') }}</div>
              </v-col>
            </v-row>

            <div v-if="profile.learning.enrolled_subjects?.length" class="mb-4">
              <div class="text-caption text-medium-emphasis mb-2">{{ $t('teacher.students.enrolledSubjects') }}</div>
              <v-chip
                v-for="subj in profile.learning.enrolled_subjects"
                :key="subj"
                size="small"
                variant="tonal"
                class="me-1 mb-1"
              >
                {{ subj }}
              </v-chip>
            </div>

            <TeacherTable v-if="profile.learning.courses?.length" class="courses-table mb-0">
              <thead>
                <tr>
                  <th>{{ $t('teacher.labels.subject') }}</th>
                  <th>{{ $t('teacher.labels.progress') }}</th>
                  <th>{{ $t('teacher.labels.subscription') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in profile.learning.courses" :key="c.course_id">
                  <td>
                    <div class="font-weight-medium">{{ c.title }}</div>
                    <div class="text-caption text-medium-emphasis">{{ $t('teacher.students.subjectGradeCaption', { subject: c.subject_name, grade: c.grade }) }}</div>
                  </td>
                  <td>{{ c.completed_lessons }}/{{ c.total_lessons }} ({{ c.progress_percent }}%)</td>
                  <td>
                    <v-chip size="x-small" variant="tonal">{{ subscriptionLabel(c.subscription_status) }}</v-chip>
                  </td>
                </tr>
              </tbody>
            </TeacherTable>
          </v-card>

          <!-- Quiz analytics -->
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-h6 font-weight-bold mb-4">{{ $t('teacher.students.quizAnalytics') }}</h3>
            <v-row dense class="mb-4">
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold">{{ profile.quiz_analytics.total_completed }}</div>
                <div class="text-caption">{{ $t('teacher.students.quizzesCompleted') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-primary">{{ profile.quiz_analytics.average_score_percent }}%</div>
                <div class="text-caption">{{ $t('teacher.students.avgResult') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-success">{{ profile.quiz_analytics.best_score_percent }}%</div>
                <div class="text-caption">{{ $t('teacher.students.bestResult') }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-h5 font-weight-bold text-error">{{ profile.quiz_analytics.lowest_score_percent }}%</div>
                <div class="text-caption">{{ $t('teacher.students.lowestResult') }}</div>
              </v-col>
            </v-row>

            <TeacherTable v-if="profile.quiz_analytics.recent_attempts?.length">
              <thead>
                <tr>
                  <th>{{ $t('teacher.labels.quiz') }}</th>
                  <th>{{ $t('teacher.labels.subject') }}</th>
                  <th>{{ $t('teacher.labels.result') }}</th>
                  <th>{{ $t('teacher.labels.date') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in profile.quiz_analytics.recent_attempts" :key="`${a.source}-${a.id}`">
                  <td>{{ a.quiz_title }}</td>
                  <td class="text-caption">{{ a.subject_name }}</td>
                  <td>
                    <v-chip size="x-small" :color="a.score_percent >= 60 ? 'success' : 'warning'" variant="tonal">
                      {{ a.score_percent }}%
                    </v-chip>
                  </td>
                  <td class="text-caption">{{ formatDate(a.submitted_at) }}</td>
                </tr>
              </tbody>
            </TeacherTable>
            <p v-else class="text-caption text-medium-emphasis text-center py-4">{{ $t('teacher.students.noQuizAttempts') }}</p>
          </v-card>

          <!-- Activity timeline -->
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-h6 font-weight-bold mb-4">{{ $t('teacher.analytics.recentActivity') }}</h3>
            <v-timeline v-if="profile.activity_timeline?.length" side="end" density="compact" truncate-line="both">
              <v-timeline-item
                v-for="ev in profile.activity_timeline"
                :key="ev.id"
                :dot-color="activityColor(ev.event_type)"
                size="small"
              >
                <div class="font-weight-medium">{{ ev.title }}</div>
                <div v-if="ev.description" class="text-caption text-medium-emphasis">{{ ev.description }}</div>
                <div class="text-caption">{{ formatDate(ev.occurred_at) }}</div>
              </v-timeline-item>
            </v-timeline>
            <p v-else class="text-caption text-medium-emphasis text-center py-4">{{ $t('teacher.students.noActivity') }}</p>
          </v-card>

          <!-- Teacher private notes -->
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <div class="d-flex align-center justify-space-between mb-4">
              <div>
                <h3 class="text-h6 font-weight-bold mb-0">{{ $t('teacher.students.privateNotes') }}</h3>
                <p class="text-caption text-medium-emphasis mb-0">{{ $t('teacher.students.privateNotesHint') }}</p>
              </div>
              <v-btn size="small" class="btn-glow" rounded="lg" @click="openNoteDialog()">
                <v-icon start>mdi-plus</v-icon>
                {{ $t('teacher.actions.addNote') }}
              </v-btn>
            </div>

            <v-alert v-if="noteError" type="error" variant="tonal" density="compact" class="mb-3">{{ noteError }}</v-alert>

            <v-card
              v-for="note in notes"
              :key="note.id"
              variant="tonal"
              class="pa-4 mb-3 rounded-lg"
            >
              <p class="text-body-2 mb-2">{{ note.note_text }}</p>
              <div class="d-flex align-center justify-space-between">
                <span class="text-caption text-medium-emphasis">{{ formatDate(note.updated_at) }}</span>
                <div>
                  <v-btn icon size="x-small" variant="text" @click="openNoteDialog(note)">
                    <v-icon size="18">mdi-pencil-outline</v-icon>
                  </v-btn>
                  <v-btn icon size="x-small" variant="text" color="error" @click="confirmDeleteNote(note)">
                    <v-icon size="18">mdi-delete-outline</v-icon>
                  </v-btn>
                </div>
              </div>
            </v-card>

            <p v-if="!notes.length" class="text-caption text-medium-emphasis text-center py-4">
              {{ $t('teacher.students.noPrivateNotes') }}
            </p>
          </v-card>

          <!-- Smart planner (read-only) -->
          <v-card class="glass-card pa-5 mb-4" variant="flat">
            <h3 class="text-h6 font-weight-bold mb-4">{{ $t('teacher.students.smartPlanner') }}</h3>
            <v-skeleton-loader v-if="plannerLoading" type="paragraph" />
            <PlannerIntelligencePanel v-else-if="plannerData" :data="plannerData" read-only />
            <p v-else class="text-caption text-medium-emphasis text-center py-4">{{ $t('teacher.students.noPlanner') }}</p>
          </v-card>

          <TeacherParentNotesSection :student-id="studentId" class="mb-4" />
        </v-col>
      </v-row>
    </template>

    <!-- Note dialog -->
    <v-dialog v-model="noteDialog" max-width="480" persistent>
      <v-card class="pa-5 rounded-xl" dir="rtl">
        <v-card-title class="px-0">{{ editingNote ? $t('teacher.students.editNoteTitle') : $t('teacher.students.newNote') }}</v-card-title>
        <v-textarea
          v-model="noteText"
          :label="$t('teacher.labels.noteText')"
          variant="outlined"
          rows="4"
          auto-grow
          rounded="lg"
          :disabled="noteSaving"
        />
        <v-card-actions class="px-0 pt-2">
          <v-spacer />
          <v-btn variant="text" :disabled="noteSaving" @click="noteDialog = false">{{ $t('common.cancel') }}</v-btn>
          <v-btn class="btn-glow" :loading="noteSaving" rounded="lg" @click="saveNote">{{ $t('common.save') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import TeacherParentNotesSection from '../../components/teacher/TeacherParentNotesSection.vue'
import TeacherStudentInsightPanel from '../../components/teacher/TeacherStudentInsightPanel.vue'
import TeacherStudentParentContactSection from '../../components/teacher/TeacherStudentParentContactSection.vue'
import { TeacherTable } from '../../components/teacher/design-system/index.js'
import PlannerIntelligencePanel from '../../components/planner/PlannerIntelligencePanel.vue'
import {
  createTeacherStudentNote,
  deleteTeacherStudentNote,
  fetchTeacherStudentProfile,
  updateTeacherStudentNote,
} from '../../api/teacherStudents.js'
import { fetchTeacherStudentPlannerApi } from '../../api/planner.js'
import { getErrorMessage } from '../../api/client.js'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const profile = ref(null)
const notes = ref([])
const plannerData = ref(null)
const plannerLoading = ref(false)

const noteDialog = ref(false)
const noteText = ref('')
const editingNote = ref(null)
const noteSaving = ref(false)
const noteError = ref('')

let loadSeq = 0

const studentId = computed(() => Number(route.params.studentId))

const summaryCards = computed(() => {
  const a = profile.value?.analytics
  if (!a) return []
  return [
    { id: 'completion', label: t('teacher.quizzes.completionRate'), value: `${a.completion_percent}%`, icon: 'mdi-chart-donut', color: 'primary' },
    { id: 'score', label: t('teacher.students.avgScoreLabel'), value: `${a.average_score_percent}%`, icon: 'mdi-school', color: 'secondary' },
    { id: 'activity', label: t('teacher.students.studyActivity'), value: String(a.total_study_activity), icon: 'mdi-book-open-page-variant', color: 'success' },
    { id: 'streak', label: t('teacher.students.streak'), value: t('teacher.labels.dayCount', { count: a.active_streak }), icon: 'mdi-fire', color: 'warning' },
    { id: 'last', label: t('teacher.labels.lastActivity'), value: formatDateShort(a.last_active_date), icon: 'mdi-clock-outline', color: 'info' },
  ]
})

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function formatDateShort(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function subscriptionLabel(status) {
  const map = { active: t('teacher.status.active'), expiring_soon: t('teacher.status.expiringSoon'), expired: t('teacher.status.expired'), pending: t('teacher.status.pending') }
  return map[status] || status
}

function activityColor(type) {
  if (type?.includes('quiz')) return 'primary'
  if (type?.includes('writing') || type?.includes('speaking')) return 'secondary'
  if (type?.includes('certificate')) return 'success'
  if (type?.includes('lesson')) return 'info'
  return 'grey'
}

async function loadPlanner() {
  plannerLoading.value = true
  plannerData.value = null
  try {
    plannerData.value = await fetchTeacherStudentPlannerApi(studentId.value)
  } catch {
    plannerData.value = null
  } finally {
    plannerLoading.value = false
  }
}

async function load() {
  const seq = ++loadSeq
  loading.value = true
  error.value = ''
  try {
    const data = await fetchTeacherStudentProfile(studentId.value)
    if (seq !== loadSeq) return
    profile.value = data
    notes.value = data.notes || []
    loadPlanner()
  } catch (e) {
    if (seq !== loadSeq) return
    error.value = getErrorMessage(e, t('teacher.errors.loadStudentProfile'))
    profile.value = null
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

function openNoteDialog(note = null) {
  editingNote.value = note
  noteText.value = note?.note_text || ''
  noteError.value = ''
  noteDialog.value = true
}

async function saveNote() {
  const text = noteText.value?.trim()
  if (!text) {
    noteError.value = t('teacher.validation.enterNote')
    return
  }
  noteSaving.value = true
  noteError.value = ''
  try {
    if (editingNote.value) {
      const updated = await updateTeacherStudentNote(studentId.value, editingNote.value.id, text)
      notes.value = notes.value.map((n) => (n.id === updated.id ? updated : n))
    } else {
      const created = await createTeacherStudentNote(studentId.value, text)
      notes.value = [created, ...notes.value]
    }
    noteDialog.value = false
  } catch (e) {
    noteError.value = getErrorMessage(e, t('teacher.errors.saveNote'))
  } finally {
    noteSaving.value = false
  }
}

async function confirmDeleteNote(note) {
  if (!window.confirm(t('teacher.confirm.deleteNote'))) return
  noteError.value = ''
  try {
    await deleteTeacherStudentNote(studentId.value, note.id)
    notes.value = notes.value.filter((n) => n.id !== note.id)
  } catch (e) {
    noteError.value = getErrorMessage(e, t('teacher.errors.deleteNote'))
  }
}

watch(
  () => route.params.studentId,
  () => load(),
  { immediate: true },
)
</script>

<style scoped>
.gap-4 {
  gap: 16px;
}
.courses-table th {
  font-weight: 700;
}
</style>
