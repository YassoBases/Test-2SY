<template>
  <v-card
    v-if="hasLesson"
    class="glass-card course-current-lesson"
    variant="flat"
  >
    <div class="course-current-lesson__inner pa-4 pa-md-5">
      <div class="course-current-lesson__lead">
        <div class="course-current-lesson__icon" aria-hidden="true">
          <v-icon size="22" color="primary">mdi-play-circle</v-icon>
        </div>
        <div class="course-current-lesson__body min-w-0">
          <p class="course-current-lesson__eyebrow">{{ eyebrowLabel }}</p>
          <h2 class="course-current-lesson__title text-truncate">{{ lessonTitle }}</h2>
          <p class="course-current-lesson__meta">
            <span>{{ t('student.course.current.withTeacher', { teacher: teacherName }) }}</span>
            <span v-if="progressContext" class="course-current-lesson__sep">·</span>
            <span v-if="progressContext">{{ progressContext }}</span>
          </p>
        </div>
      </div>

      <div class="course-current-lesson__actions">
        <v-btn
          color="secondary"
          variant="flat"
          size="large"
          rounded="lg"
          class="course-current-lesson__cta btn-glow"
          prepend-icon="mdi-play"
          :disabled="!lessonId"
          @click="$emit('continue')"
        >
          {{ ctaLabel }}
        </v-btn>
      </div>
    </div>
  </v-card>

  <v-card
    v-else-if="lessonCount === 0"
    class="glass-card course-current-lesson course-current-lesson--empty"
    variant="flat"
  >
    <div class="course-current-lesson__inner pa-4 pa-md-5 text-center">
      <v-icon size="36" color="secondary" class="mb-2 opacity-80">mdi-book-open-page-variant-outline</v-icon>
      <p class="course-current-lesson__title mb-1">{{ t('student.course.current.empty.title') }}</p>
      <p class="course-current-lesson__meta mb-0">{{ t('student.course.current.empty.subtitle') }}</p>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  lesson: { type: Object, default: null },
  teacherName: { type: String, default: '' },
  subjectName: { type: String, default: '' },
  lessonCount: { type: Number, default: 0 },
  completedLessonCount: { type: Number, default: 0 },
  progressPercent: { type: Number, default: 0 },
  allCompleted: { type: Boolean, default: false },
})

defineEmits(['continue'])

const hasLesson = computed(() => !!props.lesson?.id)

const lessonId = computed(() => props.lesson?.id ?? null)

const lessonTitle = computed(() => props.lesson?.title || '—')

const lessonPosition = computed(() => {
  if (!props.lesson?.journeyIndex || !props.lessonCount) return null
  return t('student.course.current.position', { n: props.lesson.journeyIndex, total: props.lessonCount })
})

const progressContext = computed(() => {
  if (lessonPosition.value) return lessonPosition.value
  const total = props.lessonCount
  const done = props.completedLessonCount
  if (total > 0 && done > 0) {
    return t('student.course.current.progress.lessonsCompleted', { done, total })
  }
  const pct = Math.round(props.progressPercent || 0)
  if (pct > 0) return t('student.course.hero.progress.percentOfSubject', { pct })
  return props.subjectName || ''
})

const eyebrowLabel = computed(() => {
  if (props.allCompleted) return t('student.course.current.eyebrow.allDone')
  if (props.lesson?.journeyState === 'current') return t('student.course.current.eyebrow.current')
  return t('student.course.current.eyebrow.continue')
})

const ctaLabel = computed(() => {
  if (props.allCompleted) return t('student.course.current.cta.review')
  if (props.completedLessonCount === 0) return t('student.course.current.cta.start')
  return t('student.course.current.cta.continue')
})
</script>
