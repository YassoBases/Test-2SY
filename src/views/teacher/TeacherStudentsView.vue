<template>
  <div class="slide-up-enter-active" dir="rtl">
    <PageHeader
      :eyebrow="$t('teacher.students.eyebrow')"
      :title="$t('teacher.labels.students')"
      :subtitle="$t('teacher.students.subtitle')"
    />

    <v-card class="glass-card pa-4 mb-5" variant="flat">
      <v-row dense align="center">
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            :label="$t('teacher.students.searchPlaceholder')"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            rounded="lg"
          />
        </v-col>
        <v-col cols="6" md="3">
          <v-select
            v-model="gradeFilter"
            :items="gradeItems"
            :label="$t('teacher.labels.grade')"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            rounded="lg"
          />
        </v-col>
        <v-col cols="6" md="3">
          <v-select
            v-model="subjectFilter"
            :items="subjectItems"
            item-title="label"
            item-value="value"
            :label="$t('teacher.students.subjectOptional')"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            rounded="lg"
          />
        </v-col>
        <v-col cols="12" md="2" class="text-md-end">
          <v-chip size="small" variant="tonal" color="primary">
            {{ $t('teacher.labels.studentCount', { count: total }) }}
          </v-chip>
        </v-col>
      </v-row>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <LoadingState v-if="loading" variant="table" :count="1" class="mb-4" />

    <EmptyState
      v-else-if="!students.length"
      :preset="hasFilters ? 'studentsFiltered' : 'students'"
      class="mb-4"
    />

    <v-card v-else class="glass-card" variant="flat">
      <TeacherTable class="students-table">
        <thead>
          <tr>
            <th>{{ $t('teacher.labels.student') }}</th>
            <th>{{ $t('teacher.labels.grade') }}</th>
            <th>{{ $t('teacher.labels.status') }}</th>
            <th>{{ $t('teacher.labels.lastActivity') }}</th>
            <th>{{ $t('teacher.labels.completion') }}</th>
            <th>{{ $t('teacher.analytics.avgQuiz') }}</th>
            <th class="text-end">{{ $t('teacher.labels.action') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.student_id">
            <td>
              <div class="d-flex align-center gap-3 py-2">
                <TeacherAvatar :name="s.full_name" :size="40" />
                <div>
                  <div class="font-weight-bold">{{ s.full_name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ s.email }}</div>
                </div>
              </div>
            </td>
            <td>{{ s.grade ? $t('teacher.labels.gradeNumber', { grade: s.grade }) : '—' }}</td>
            <td>
              <v-chip size="x-small" :color="s.is_active ? 'success' : 'warning'" variant="tonal">
                {{ s.is_active ? $t('teacher.status.active') : $t('teacher.status.expired') }}
              </v-chip>
            </td>
            <td class="text-caption">{{ formatDate(s.last_activity_at) }}</td>
            <td>
              <div class="d-flex align-center gap-2">
                <v-progress-linear
                  :model-value="s.completion_percent"
                  color="primary"
                  height="6"
                  rounded
                  style="min-width: 64px; max-width: 80px"
                />
                <span class="text-caption">{{ s.completion_percent }}%</span>
              </div>
            </td>
            <td>{{ s.avg_quiz_percent }}%</td>
            <td class="text-end">
              <v-btn
                size="small"
                class="btn-glow"
                rounded="lg"
                :to="{ name: 'teacher-student-profile', params: { studentId: s.student_id } }"
              >
                {{ $t('teacher.actions.viewProfile') }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </TeacherTable>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRoute } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import { TeacherTable } from '../../components/teacher/design-system/index.js'
import { fetchTeacherGrades } from '../../api/teacherDashboard.js'
import { searchTeacherStudents } from '../../api/teacherStudents.js'
import { getErrorMessage } from '../../api/client.js'
import { ACADEMIC_GRADES } from '../../constants/app.js'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const students = ref([])
const total = ref(0)
const searchQuery = ref('')
const gradeFilter = ref(null)
const subjectFilter = ref(null)
const subjectItems = ref([])
let debounceTimer = null
let loadSeq = 0

const gradeItems = ACADEMIC_GRADES.map((g) => ({ title: t('teacher.labels.gradeNumber', { grade: g }), value: g }))

const hasFilters = computed(
  () => Boolean(searchQuery.value?.trim() || gradeFilter.value || subjectFilter.value),
)

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('ar-SY', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

async function loadSubjects() {
  try {
    const grades = await fetchTeacherGrades()
    const seen = new Map()
    for (const c of grades.courses || []) {
      if (!seen.has(c.subject_id)) {
        seen.set(c.subject_id, { value: c.subject_id, label: c.subject_name })
      }
    }
    subjectItems.value = [...seen.values()]
  } catch {
    subjectItems.value = []
  }
}

async function load() {
  const seq = ++loadSeq
  loading.value = true
  error.value = ''
  try {
    const params = {}
    const q = searchQuery.value?.trim()
    if (q) params.q = q
    if (gradeFilter.value) params.grade = gradeFilter.value
    if (subjectFilter.value) params.subject_id = subjectFilter.value
    const data = await searchTeacherStudents(params)
    if (seq !== loadSeq) return
    students.value = data.students || []
    total.value = data.total ?? students.value.length
  } catch (e) {
    if (seq !== loadSeq) return
    error.value = getErrorMessage(e, t('teacher.errors.loadStudents'))
    students.value = []
    total.value = 0
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

function scheduleLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(load, 300)
}

watch([searchQuery, gradeFilter, subjectFilter], scheduleLoad)

function applyRouteFilters() {
  const grade = Number(route.query.grade)
  if (Number.isFinite(grade) && grade >= 1 && grade <= 12) {
    gradeFilter.value = grade
  }
  const subjectId = Number(route.query.subject_id)
  if (Number.isFinite(subjectId) && subjectId > 0) {
    subjectFilter.value = subjectId
  }
}

onMounted(async () => {
  await loadSubjects()
  applyRouteFilters()
  await load()
})
</script>

<style scoped>
.students-table th {
  font-weight: 700;
  white-space: nowrap;
}
.gap-3 {
  gap: 12px;
}
.gap-2 {
  gap: 8px;
}
</style>



