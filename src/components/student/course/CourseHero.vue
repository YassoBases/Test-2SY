<template>
  <v-card class="glass-card course-hero" variant="flat">
    <div class="course-hero__inner pa-4 pa-md-5">
      <div class="course-hero__lead d-flex align-start gap-3 gap-md-4">
        <TeacherAvatar
          :name="teacherName"
          :image-url="teacherImageUrl"
          :size="52"
          class="course-hero__avatar flex-shrink-0"
        />
        <div class="course-hero__identity flex-grow-1 min-width-0">
          <p class="course-hero__eyebrow">{{ subjectName }}</p>
          <h1 class="course-hero__teacher mb-1">
            {{ t('student.course.hero.withTeacher', { teacher: teacherName }) }}
          </h1>
          <p class="course-hero__welcome mb-0">
            {{ t('student.course.hero.welcome') }}
          </p>
          <p v-if="progressLine" class="course-hero__progress text-caption text-medium-emphasis mb-0 mt-2">
            {{ progressLine }}
          </p>
        </div>
      </div>

      <div v-if="canContact" class="course-hero__secondary d-flex align-center flex-wrap gap-2 gap-md-3 mt-3 pt-3">
        <v-switch
          v-if="hasLinkedParent"
          v-model="includeParentLocal"
          density="compact"
          hide-details
          color="primary"
          class="course-hero__parent-switch"
          :label="t('student.course.hero.includeParent')"
        />
        <v-spacer v-if="hasLinkedParent" class="d-none d-sm-flex" />
        <v-btn
          size="small"
          variant="text"
          rounded="lg"
          prepend-icon="mdi-message-text-outline"
          :loading="messaging"
          @click="$emit('message-teacher', { includeParent: includeParentLocal })"
        >
          {{ t('student.course.hero.messageTeacher') }}
        </v-btn>
        <v-btn
          size="small"
          variant="text"
          rounded="lg"
          prepend-icon="mdi-account-school-outline"
          @click="$emit('view-profile')"
        >
          {{ t('student.course.hero.viewProfile') }}
        </v-btn>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'

const { t } = useI18n()

const props = defineProps({
  subjectName: { type: String, default: '' },
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  progressPercent: { type: Number, default: 0 },
  completedLessonCount: { type: Number, default: 0 },
  lessonCount: { type: Number, default: 0 },
  canContact: { type: Boolean, default: true },
  hasLinkedParent: { type: Boolean, default: false },
  messaging: { type: Boolean, default: false },
})

defineEmits(['message-teacher', 'view-profile'])

const includeParentLocal = ref(false)

const progressLine = computed(() => {
  const total = props.lessonCount
  const done = props.completedLessonCount
  if (total > 0) {
    if (done === 0) {
      return total === 1
        ? t('student.course.hero.progress.lessonWaiting')
        : t('student.course.hero.progress.lessonsWaiting', { count: total })
    }
    if (done >= total) return t('student.course.hero.progress.allCompleted')
    return t('student.course.hero.progress.lessonsCompleted', { done, total })
  }
  const pct = Math.round(props.progressPercent || 0)
  if (pct > 0) return t('student.course.hero.progress.percentOfSubject', { pct })
  return ''
})
</script>
