<template>
  <article class="teacher-class-workspace em-hover-lift">
    <div class="teacher-class-workspace__head">
      <div class="teacher-class-workspace__title-block">
        <h3 class="teacher-class-workspace__subject">{{ course.subject_name }}</h3>
        <p v-if="course.title" class="teacher-class-workspace__course-title">{{ course.title }}</p>
      </div>
      <div class="teacher-class-workspace__badges">
        <span class="teacher-class-workspace__badge">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</span>
        <span
          class="teacher-class-workspace__badge"
          :class="course.is_published ? 'teacher-class-workspace__badge--live' : 'teacher-class-workspace__badge--draft'"
        >
          {{ course.is_published ? $t('teacher.status.published') : $t('teacher.status.draft') }}
        </span>
      </div>
    </div>

    <div v-if="teacherName || teacherAvatar" class="teacher-class-workspace__teacher">
      <img
        v-if="teacherAvatar"
        :src="teacherAvatar"
        alt=""
        class="teacher-class-workspace__avatar"
      />
      <span v-else class="teacher-class-workspace__avatar teacher-class-workspace__avatar--initials">
        {{ teacherInitials }}
      </span>
      <span class="teacher-class-workspace__teacher-name">{{ teacherName }}</span>
    </div>

    <div class="teacher-class-workspace__meta">
      <span class="teacher-class-workspace__meta-item">
        <v-icon size="14">mdi-account-group-outline</v-icon>
        {{ $t('teacher.labels.studentCount', { count: course.subscribed_students }) }}
      </span>
      <span class="teacher-class-workspace__meta-item">
        <v-icon size="14">mdi-book-open-variant</v-icon>
        {{ $t('teacher.labels.lessonCount', { count: course.lesson_count }) }}
      </span>
      <span class="teacher-class-workspace__meta-item">
        <v-icon size="14">mdi-clipboard-text-outline</v-icon>
        {{ $t('teacher.labels.quizCount', { count: course.quiz_count ?? 0 }) }}
      </span>
      <span class="teacher-class-workspace__meta-item">
        <v-icon size="14">mdi-tag-outline</v-icon>
        {{ priceLabel }}
      </span>
    </div>

    <div class="teacher-class-workspace__progress">
      <div class="teacher-class-workspace__progress-label">
        <span>{{ progressLabel }}</span>
        <span>{{ course.completion_percent }}%</span>
      </div>
      <div class="teacher-class-workspace__progress-track" aria-hidden="true">
        <div
          class="teacher-class-workspace__progress-fill"
          :style="{ width: `${Math.min(100, Math.max(0, course.completion_percent || 0))}%` }"
        />
      </div>
    </div>

    <div class="teacher-class-workspace__footer">
      <v-btn
        class="btn-glow"
        color="secondary"
        variant="flat"
        block
        rounded="lg"
        size="default"
        :to="coursePath"
      >
        {{ $t('teacher.actions.followUp') }}
        <v-icon end size="18">mdi-arrow-left</v-icon>
      </v-btn>

      <div class="teacher-class-workspace__actions-secondary">
        <router-link :to="coursePath" class="teacher-class-workspace__action-link" @click.stop>
          <v-icon size="14">mdi-pencil-outline</v-icon>
          {{ $t('common.edit') }}
        </router-link>
        <router-link :to="coursePath" class="teacher-class-workspace__action-link" @click.stop>
          <v-icon size="14">mdi-account-school-outline</v-icon>
          {{ $t('teacher.labels.students') }}
        </router-link>
        <router-link :to="ROUTES.TEACHER_MESSAGES" class="teacher-class-workspace__action-link" @click.stop>
          <v-icon size="14">mdi-message-text-outline</v-icon>
          {{ $t('teacher.labels.messages') }}
        </router-link>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { ROUTES } from '../../../constants/app.js'

const props = defineProps({
  course: { type: Object, required: true },
  teacherName: { type: String, default: '' },
  teacherAvatar: { type: String, default: '' },
})

const coursePath = computed(() => `/teacher/grades/${props.course.course_id}`)

const teacherInitials = computed(() => {
  const n = props.teacherName.trim()
  if (!n) return t('teacher.labels.teacherInitial')
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`
  return n.slice(0, 2)
})

const progressLabel = computed(() => {
  const n = props.course.lesson_count || 0
  if (n === 0) return t('teacher.grades.noLessonsYet')
  if (n === 1) return t('teacher.grades.oneLessonPublished')
  return t('teacher.labels.lessonsPublished', { count: n })
})

const priceLabel = computed(() => {
  const v = Number(props.course.price)
  if (!v) return t('teacher.labels.free')
  return t('teacher.labels.currencySyp', { amount: v.toLocaleString('ar-SY') })
})
</script>
