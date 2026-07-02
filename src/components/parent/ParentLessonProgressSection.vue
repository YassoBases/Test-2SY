<template>
  <div v-if="summary" class="lesson-progress-page">
    <v-row dense class="mb-4">
      <v-col v-for="card in statusCards" :key="card.key" cols="6" sm="3">
        <v-card
          class="kpi-chip pa-3 rounded-lg h-100"
          :class="{ 'kpi-chip--active': activeFilter === card.key }"
          variant="flat"
          @click="toggleFilter(card.key)"
        >
          <div class="d-flex align-center gap-2 mb-1">
            <v-icon :color="card.color" size="18">{{ card.icon }}</v-icon>
            <span class="text-caption font-weight-bold">{{ card.label }}</span>
          </div>
          <div class="text-h5 font-weight-bold">{{ card.count }}</div>
          <div class="text-caption text-medium-emphasis">{{ card.hint }}</div>
        </v-card>
      </v-col>
      <v-col cols="6" sm="3">
        <v-card class="kpi-chip kpi-chip--rate pa-3 rounded-lg h-100" variant="flat">
          <div class="d-flex align-center gap-2 mb-1">
            <v-icon color="primary" size="18">mdi-chart-donut</v-icon>
            <span class="text-caption font-weight-bold">{{ t('parent.lessons.progress.completionRate') }}</span>
          </div>
          <div class="text-h5 font-weight-bold text-primary">{{ summary.completion_rate ?? 0 }}%</div>
          <div class="text-caption text-medium-emphasis">{{ t('parent.lessons.progress.lessonCount', { n: summary.total_lessons ?? 0 }) }}</div>
        </v-card>
      </v-col>
    </v-row>

    <section
      v-for="course in filteredCourses"
      :key="course.course_id"
      class="course-section mb-4"
    >
      <div class="course-header pa-3 pa-md-4 rounded-lg mb-3">
        <div class="d-flex align-start justify-space-between flex-wrap gap-2 mb-2">
          <div>
            <h4 class="text-subtitle-1 font-weight-bold mb-0">
              {{ course.subject_name || course.course_title }}
            </h4>
            <p v-if="course.course_title && course.subject_name !== course.course_title" class="text-caption text-medium-emphasis mb-0 mt-1">
              {{ course.course_title }}
            </p>
          </div>
          <div class="d-flex flex-wrap gap-1">
            <v-chip
              v-if="course.in_progress_count"
              size="x-small"
              color="warning"
              variant="tonal"
              prepend-icon="mdi-alert-circle-outline"
            >
              {{ t('parent.lessons.progress.needsFollowUp', { n: course.in_progress_count }) }}
            </v-chip>
            <v-chip
              v-else-if="course.progress_percent >= 80"
              size="x-small"
              color="success"
              variant="tonal"
              prepend-icon="mdi-trending-up"
            >
              {{ t('parent.lessons.progress.excellentProgress') }}
            </v-chip>
          </div>
        </div>

        <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-2">
          <span class="text-h6 font-weight-bold" :class="courseProgressClass(course)">
            {{ t('parent.lessons.progress.percentComplete', { percent: course.progress_percent }) }}
          </span>
          <span class="text-caption text-medium-emphasis">
            {{ t('parent.lessons.progress.lessonsOf', { completed: course.completed_count, total: course.total_lessons }) }}
          </span>
        </div>

        <v-progress-linear
          :model-value="course.progress_percent"
          :color="course.progress_percent >= 70 ? 'success' : course.progress_percent >= 30 ? 'warning' : 'primary'"
          height="8"
          rounded
        />
      </div>

      <v-row dense>
        <v-col
          v-for="lesson in filteredLessons(course.lessons)"
          :key="lesson.lesson_id"
          cols="12"
          sm="6"
          lg="4"
        >
          <ParentLessonCard :lesson="lesson" @open="$emit('open-lesson', $event)" />
        </v-col>
      </v-row>
    </section>

    <v-alert v-if="!filteredCourses.length" type="info" variant="tonal" class="rounded-lg">
      {{ t('parent.lessons.progress.noLessonsInFilter') }}
    </v-alert>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentLessonCard from './ParentLessonCard.vue'

const props = defineProps({
  summary: { type: Object, default: null },
  courses: { type: Array, default: () => [] },
})

defineEmits(['open-lesson'])

const { t } = useI18n()

const activeFilter = ref('all')

const statusCards = computed(() => [
  {
    key: 'completed',
    icon: 'mdi-check-circle-outline',
    label: t('parent.lessons.progress.completed'),
    count: props.summary?.completed_lessons ?? 0,
    hint: t('parent.lessons.progress.finishedLessons'),
    color: 'success',
  },
  {
    key: 'in_progress',
    icon: 'mdi-progress-clock',
    label: t('parent.lessons.progress.inProgress'),
    count: props.summary?.in_progress_lessons ?? 0,
    hint: t('parent.lessons.progress.needsFollowUpOne'),
    color: 'warning',
  },
  {
    key: 'pending',
    icon: 'mdi-circle-outline',
    label: t('parent.lessons.progress.notStarted'),
    count: props.summary?.pending_lessons ?? 0,
    hint: t('parent.lessons.progress.notOpenedYet'),
    color: 'default',
  },
])

const filteredCourses = computed(() => {
  if (activeFilter.value === 'all') return props.courses
  return props.courses
    .map((c) => ({
      ...c,
      lessons: (c.lessons || []).filter((l) => l.status === activeFilter.value),
    }))
    .filter((c) => c.lessons.length)
})

function filteredLessons(lessons) {
  if (activeFilter.value === 'all') return lessons || []
  return (lessons || []).filter((l) => l.status === activeFilter.value)
}

function toggleFilter(key) {
  activeFilter.value = activeFilter.value === key ? 'all' : key
}

function courseProgressClass(course) {
  if (course.progress_percent >= 70) return 'text-success'
  if (course.progress_percent >= 30) return 'text-warning'
  return 'text-primary'
}
</script>

<style scoped>
.lesson-progress-page {
  margin-top: 0.25rem;
}

.kpi-chip {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.kpi-chip--active {
  border-color: rgba(124, 108, 240, 0.55);
  background: rgba(124, 108, 240, 0.1);
}

.kpi-chip--rate {
  cursor: default;
}

.course-section {
  margin-bottom: 1rem;
}

.course-header {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
}
</style>
