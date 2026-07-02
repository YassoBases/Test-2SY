<template>
  <div class="teacher-classes-page slide-up-enter-active">
    <PageHeader
      :eyebrow="$t('teacher.grades.eyebrow')"
      :title="$t('teacher.grades.title')"
      :subtitle="$t('teacher.grades.subtitle')"
    >
      <template #actions>
        <v-btn class="btn-glow" rounded="lg" @click="showCreate = true">
          <v-icon start>mdi-plus-circle</v-icon>
          {{ $t('teacher.actions.createNewClass') }}
        </v-btn>
      </template>
    </PageHeader>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>

    <template v-if="!loading && courses.length">
      <TeacherClassFilters
        v-model="activeFilter"
        :grade-options="gradeOptions"
        :subject-options="subjectOptions"
        :counts="filterCounts"
      />
    </template>

    <LoadingState v-if="loading" variant="cards" :count="6" class="mb-4" />

    <AppSection
      v-else-if="courses.length"
      :title="$t('teacher.grades.sectionTitle')"
      :subtitle="sectionSubtitle"
      spacing="sm"
      :divider="false"
    >
      <div v-if="filteredCourses.length" class="teacher-class-grid">
        <TeacherClassWorkspaceCard
          v-for="c in filteredCourses"
          :key="c.course_id"
          :course="c"
          :teacher-name="teacherDisplayName"
          :teacher-avatar="teacherAvatarUrl"
        />
      </div>

      <div v-else class="teacher-classes-empty teacher-classes-empty--filtered">
        <p class="teacher-classes-empty__title mb-1">{{ $t('teacher.grades.noFilterMatch') }}</p>
        <p class="teacher-classes-empty__desc mb-3">{{ $t('teacher.grades.tryOtherFilter') }}</p>
        <v-btn variant="tonal" size="small" rounded="lg" @click="activeFilter = 'all'">
          {{ $t('teacher.actions.viewAll') }}
        </v-btn>
      </div>
    </AppSection>

    <div v-else class="teacher-classes-empty">
      <span class="teacher-classes-empty__icon" aria-hidden="true">
        <v-icon size="32">mdi-school-outline</v-icon>
      </span>
      <h2 class="teacher-classes-empty__title">{{ $t('teacher.grades.noClassesYet') }}</h2>
      <p class="teacher-classes-empty__desc">
        {{ $t('teacher.grades.createFirstHint') }}
      </p>
      <v-btn class="btn-glow" rounded="lg" size="large" @click="showCreate = true">
        <v-icon start>mdi-plus</v-icon>
        {{ $t('teacher.actions.createNewClass') }}
      </v-btn>
    </div>

    <CreateCourseDialog v-model="showCreate" @created="onCourseCreated" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRouter } from 'vue-router'
import PageHeader from '../../components/common/PageHeader.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import CreateCourseDialog from '../../components/teacher/CreateCourseDialog.vue'
import TeacherClassFilters from '../../components/teacher/classes/TeacherClassFilters.vue'
import TeacherClassWorkspaceCard from '../../components/teacher/classes/TeacherClassWorkspaceCard.vue'
import { AppSection } from '../../components/ui/index.js'
import { fetchTeacherGrades } from '../../api/teacherDashboard.js'
import { fetchTeacherManualQuizzes } from '../../api/manualQuizzes.js'
import { getApiBaseUrl, getErrorMessage } from '../../api/client.js'
import { useAuth } from '../../composables/useAuth.js'
import { ensureTeacherProfile } from '../../composables/useTeacherProfile.js'
import '../../assets/styles/teacher-classes.css'

const router = useRouter()
const { user } = useAuth()

const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const courses = ref([])
const activeFilter = ref('all')
const teacherAvatarUrl = ref('')
const teacherDisplayName = ref('')

const gradeOptions = computed(() => {
  const grades = [...new Set(courses.value.map((c) => c.grade))].filter((g) => g != null)
  return grades.sort((a, b) => Number(a) - Number(b))
})

const subjectOptions = computed(() => {
  const map = new Map()
  for (const c of courses.value) {
    if (!map.has(c.subject_id)) {
      map.set(c.subject_id, { id: c.subject_id, name: c.subject_name })
    }
  }
  return [...map.values()].sort((a, b) => a.name.localeCompare(b.name, 'ar'))
})

const filterCounts = computed(() => {
  const counts = {
    all: courses.value.length,
    published: courses.value.filter((c) => c.is_published).length,
    draft: courses.value.filter((c) => !c.is_published).length,
  }
  for (const g of gradeOptions.value) {
    counts[`grade:${g}`] = courses.value.filter((c) => c.grade === g).length
  }
  for (const s of subjectOptions.value) {
    counts[`subject:${s.id}`] = courses.value.filter((c) => c.subject_id === s.id).length
  }
  return counts
})

const filteredCourses = computed(() => {
  const f = activeFilter.value
  if (f === 'all') return courses.value
  if (f === 'published') return courses.value.filter((c) => c.is_published)
  if (f === 'draft') return courses.value.filter((c) => !c.is_published)
  if (f.startsWith('grade:')) {
    const grade = Number(f.slice(6))
    return courses.value.filter((c) => Number(c.grade) === grade)
  }
  if (f.startsWith('subject:')) {
    const id = Number(f.slice(8))
    return courses.value.filter((c) => c.subject_id === id)
  }
  return courses.value
})

const sectionSubtitle = computed(() => {
  const n = filteredCourses.value.length
  if (activeFilter.value === 'all') {
    return n === 1 ? t('teacher.grades.oneActiveClass') : t('teacher.grades.activeClassesCount', { count: n })
  }
  return t('teacher.grades.activeOfTotal', { active: n, total: courses.value.length })
})

function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = getApiBaseUrl().replace(/\/api$/, '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

function onCourseCreated(course) {
  router.push(`/teacher/grades/${course.id}`)
}

async function enrichWithQuizCounts(list) {
  return Promise.all(
    list.map(async (course) => {
      try {
        const quizzes = await fetchTeacherManualQuizzes(course.course_id)
        return { ...course, quiz_count: quizzes.length }
      } catch {
        return { ...course, quiz_count: 0 }
      }
    }),
  )
}

async function loadTeacherIdentity() {
  teacherDisplayName.value = user.value?.name || ''
  try {
    const profile = await ensureTeacherProfile()
    if (profile.full_name) teacherDisplayName.value = profile.full_name
    if (profile.image_url) teacherAvatarUrl.value = mediaUrl(profile.image_url)
  } catch {
    /* fallback to session name */
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchTeacherGrades()
    const list = data?.courses || []
    courses.value = list.length ? await enrichWithQuizCounts(list) : []
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadGrades'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadTeacherIdentity()])
})
</script>
