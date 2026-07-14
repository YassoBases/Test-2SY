<template>
  <div class="slide-up-enter-active" dir="rtl">
    <PageHeader :eyebrow="$t('teacher.lessons.eyebrow')" :title="$t('teacher.labels.lessons')" :subtitle="$t('teacher.lessons.subtitle')" />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4 rounded-lg">{{ error }}</v-alert>
    <LoadingState v-if="loading" variant="table" :count="1" class="mb-4" />

    <EmptyState v-else-if="!lessons.length" preset="lessons" class="mb-4" />

    <section v-else class="lesson-workspace-panel">
      <TeacherLessonWorkspaceToolbar
        v-model:search="lessonSearch"
        :count="lessons.length"
        :show-filter-shell="true"
      />

      <div v-if="!filteredLessons.length" class="lesson-workspace-empty">
        <p class="lesson-workspace-empty__desc mb-0">{{ $t('teacher.grades.noLessonMatch') }}</p>
      </div>

      <div v-else class="lesson-workspace-list">
        <TeacherLessonWorkspaceRow
          v-for="l in filteredLessons"
          :key="`${l.course_id}-${l.id}`"
          :lesson="l"
          :preview-to="previewLink(l)"
          :edit-to="editLink(l)"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import TeacherLessonWorkspaceRow from '../../components/teacher/lessons/TeacherLessonWorkspaceRow.vue'
import TeacherLessonWorkspaceToolbar from '../../components/teacher/lessons/TeacherLessonWorkspaceToolbar.vue'
import { fetchTeacherGrades, fetchTeacherCourseDetail } from '../../api/teacherDashboard.js'
import { getErrorMessage } from '../../api/client.js'
import '../../assets/styles/teacher-lessons.css'

const loading = ref(true)
const error = ref('')
const lessons = ref([])
const lessonSearch = ref('')

const filteredLessons = computed(() => {
  const q = lessonSearch.value.trim().toLowerCase()
  if (!q) return lessons.value
  return lessons.value.filter((l) => {
    const hay = `${l.title || ''} ${l.course_label || ''}`.toLowerCase()
    return hay.includes(q)
  })
})

function previewLink(lesson) {
  return {
    name: 'teacher-lesson-preview',
    params: { courseId: lesson.course_id, lessonId: lesson.id },
  }
}

function editLink(lesson) {
  return {
    name: 'teacher-lesson-edit',
    params: { courseId: lesson.course_id, lessonId: lesson.id },
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const grades = await fetchTeacherGrades()
    const rows = []
    for (const c of grades.courses || []) {
      const detail = await fetchTeacherCourseDetail(c.course_id)
      for (const l of detail.lessons || []) {
        rows.push({
          ...l,
          course_id: l.course_id ?? c.course_id,
          course_label: t('teacher.labels.subjectGradeDash', { subject: detail.subject_name, grade: detail.grade }),
        })
      }
    }
    lessons.value = rows
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadLessons'))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
