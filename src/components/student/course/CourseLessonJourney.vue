<template>
  <section class="course-journey" :aria-label="t('student.course.journey.ariaLabel')">
    <h2 class="course-journey__head">{{ t('student.course.journey.title') }}</h2>

    <div v-if="!lessons.length" class="course-journey__empty text-center pa-5">
      <v-icon size="36" color="secondary" class="mb-2 opacity-70">mdi-book-open-page-variant-outline</v-icon>
      <p class="text-body-2 font-weight-medium mb-1">{{ t('student.course.journey.emptyTitle') }}</p>
      <p class="text-caption text-medium-emphasis mb-0">
        {{ t('student.course.journey.emptySubtitle') }}
      </p>
    </div>

    <ol v-else class="course-journey__list">
      <li
        v-for="lesson in lessons"
        :key="lesson.id"
        class="course-journey__item"
        :class="`course-journey__item--${lesson.journeyState}`"
      >
        <div class="course-journey__rail" aria-hidden="true">
          <span class="course-journey__dot">
            <v-icon v-if="lesson.journeyState === 'completed'" size="12">mdi-check</v-icon>
            <v-icon v-else-if="lesson.journeyState === 'locked'" size="12">mdi-lock</v-icon>
            <v-icon v-else-if="lesson.journeyState === 'current'" size="12">mdi-play</v-icon>
            <span v-else class="course-journey__dot-empty" />
          </span>
          <span
            v-if="lesson.journeyIndex < lessons.length"
            class="course-journey__line"
            :class="{ 'course-journey__line--filled': lesson.journeyState === 'completed' }"
          />
        </div>

        <button
          type="button"
          class="course-journey__card"
          :disabled="lesson.journeyState === 'locked'"
          :aria-current="lesson.journeyState === 'current' ? 'step' : undefined"
          :aria-label="lessonAriaLabel(lesson)"
          @click="$emit('select', lesson)"
        >
          <span class="course-journey__card-main">
            <span class="course-journey__lesson-num">{{ t('student.course.journey.lessonNumber', { n: lesson.journeyIndex }) }}</span>
            <span class="course-journey__title">{{ lesson.title }}</span>
          </span>
          <span class="course-journey__status">{{ stateLabel(lesson.journeyState) }}</span>
        </button>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  lessons: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['select'])

const STATE_KEYS = {
  completed: 'student.course.journey.state.completed',
  current: 'student.course.journey.state.current',
  upcoming: 'student.course.journey.state.upcoming',
  locked: 'student.course.journey.state.locked',
}

function stateLabel(state) {
  const key = STATE_KEYS[state]
  return key ? t(key) : ''
}

function lessonAriaLabel(lesson) {
  const state = stateLabel(lesson.journeyState)
  return state ? `${lesson.title} — ${state}` : lesson.title
}
</script>
