<template>
  <v-card
    class="course-card glass-card h-100 d-flex flex-column"
    :class="{
      'course-card--locked': !course.unlocked,
      'course-card--unlocked': course.unlocked,
    }"
    variant="flat"
  >
    <div class="course-card__glow" />

    <v-card-text class="pa-5 d-flex flex-column flex-grow-1">
      <div class="d-flex align-start gap-3 mb-4">
        <TeacherAvatar
          :name="course.teacher_name"
          :image-url="teacherImageUrl"
          :size="52"
        />
        <div class="flex-grow-1 min-width-0">
          <div class="text-subtitle-1 font-weight-bold text-truncate">{{ course.subject_name }}</div>
          <div class="text-caption text-medium-emphasis text-truncate">{{ course.teacher_name }}</div>
        </div>
        <v-icon v-if="course.unlocked" color="success" size="26">mdi-lock-open-variant</v-icon>
        <v-icon v-else color="warning" size="26">mdi-lock</v-icon>
      </div>

      <p class="text-body-2 text-medium-emphasis mb-3 flex-grow-1 course-card__title">
        {{ course.title }}
      </p>

      <div class="d-flex flex-wrap gap-2 mb-3">
        <v-chip size="x-small" variant="tonal" color="primary">{{ t('student.course.card.grade', { grade: course.grade }) }}</v-chip>
        <v-chip size="x-small" variant="tonal">{{ t('student.course.card.lessonCount', { n: course.lesson_count }) }}</v-chip>
      </div>

      <div v-if="course.unlocked && course.progress_percent > 0" class="mb-4">
        <div class="d-flex justify-space-between text-caption mb-1">
          <span>{{ t('student.course.card.progress') }}</span>
          <span class="text-secondary font-weight-bold">{{ course.progress_percent }}%</span>
        </div>
        <v-progress-linear
          :model-value="course.progress_percent"
          height="6"
          rounded
          color="secondary"
        />
      </div>

      <div v-if="course.subscription_status === 'expiring_soon' && course.unlocked" class="mb-3">
        <v-chip size="x-small" color="warning" variant="flat" prepend-icon="mdi-clock-alert">
          {{ t('student.course.card.expiringSoon', { n: course.days_until_expiry }) }}
        </v-chip>
      </div>

      <div v-if="!course.unlocked" class="locked-overlay mb-4 locked-preview">
        <p class="text-caption text-center mb-0 font-weight-medium">
          {{ course.lock_reason || t('student.course.card.lockReason') }}
        </p>
      </div>

      <v-btn
        v-if="course.unlocked"
        block
        size="large"
        rounded="lg"
        class="btn-glow mt-auto"
        :to="courseRoute"
      >
        <v-icon start>mdi-play-circle</v-icon>
        {{ t('student.course.card.continue') }}
      </v-btn>
      <v-btn
        v-else
        block
        size="large"
        rounded="lg"
        :variant="course.subscription_status === 'expired' ? 'flat' : 'tonal'"
        :color="course.subscription_status === 'expired' ? 'warning' : 'secondary'"
        class="mt-auto"
        :to="ROUTES.STUDENT_SUBSCRIPTIONS"
      >
        <v-icon start>{{ course.subscription_status === 'expired' ? 'mdi-refresh' : 'mdi-cart' }}</v-icon>
        {{ course.subscription_status === 'expired' ? t('student.course.card.renew') : t('student.course.card.subscribe') }}
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import { ROUTES } from '../../constants/app.js'
import { teacherImageFromEntity } from '../../utils/teacherAvatar.js'

const { t } = useI18n()

const props = defineProps({
  course: { type: Object, required: true },
})

const courseRoute = computed(() => ROUTES.STUDENT_COURSE(props.course.id))
const teacherImageUrl = computed(() => teacherImageFromEntity(props.course))
</script>

<style scoped>
.course-card {
  position: relative;
  overflow: hidden;
  transition: transform 0.28s ease, box-shadow 0.28s ease;
}

.course-card--unlocked:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(34, 211, 238, 0.15) !important;
}

.course-card--locked {
  opacity: 0.92;
}

.course-card--locked .course-card__title {
  filter: blur(2px);
  user-select: none;
}

.locked-preview {
  backdrop-filter: blur(1px);
}

.course-card__glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--em-purple), var(--em-cyan), transparent);
}

.course-card--locked .course-card__glow {
  opacity: 0.35;
}

.locked-overlay {
  padding: 0.65rem;
  border-radius: 10px;
  background: rgba(251, 191, 36, 0.08);
  border: 1px dashed rgba(251, 191, 36, 0.35);
}

.course-card__title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.min-width-0 {
  min-width: 0;
}
</style>
