<template>
  <article class="student-workspace-row">
    <div class="student-workspace-row__content">
      <div class="student-workspace-row__identity">
        <span class="student-workspace-row__avatar" aria-hidden="true">{{ initials }}</span>
        <div class="student-workspace-row__identity-text">
          <router-link
            :to="profileTo"
            class="student-workspace-row__name"
          >
            {{ student.full_name }}
          </router-link>
          <span
            class="student-workspace-row__status"
            :class="`student-workspace-row__status--${student.subscription_status}`"
          >
            {{ subscriptionStatusLabel(student.subscription_status) }}
          </span>
        </div>
      </div>

      <div class="student-workspace-row__metrics">
        <div class="student-workspace-row__metric">
          <span class="student-workspace-row__metric-label">{{ $t('teacher.lessons.lessonProgress') }}</span>
          <TeacherLessonProgressMini
            :percent="student.progress_percent"
            variant="row"
          />
        </div>

        <div class="student-workspace-row__metric student-workspace-row__metric--compact">
          <span class="student-workspace-row__metric-label">{{ $t('teacher.labels.quiz') }}</span>
          <span class="student-workspace-row__metric-value">{{ student.avg_quiz_percent }}%</span>
        </div>

        <div class="student-workspace-row__metric student-workspace-row__metric--compact">
          <span class="student-workspace-row__metric-label">{{ $t('teacher.lessons.documentedCompletion') }}</span>
          <span class="student-workspace-row__metric-value">
            {{ student.verified_completions }}/{{ student.total_lessons }}
          </span>
        </div>

        <p v-if="lastActivity" class="student-workspace-row__activity">
          {{ $t('teacher.labels.lastActivityAt', { date: lastActivity }) }}
        </p>
      </div>
    </div>

    <div class="student-workspace-row__aside">
      <v-menu
        location="bottom end"
        transition="lesson-menu-transition"
        :close-on-content-click="true"
      >
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            icon
            variant="text"
            size="x-small"
            class="student-workspace-row__menu-btn"
            :aria-label="$t('teacher.lessons.studentActions')"
          >
            <v-icon size="18">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list class="lesson-workspace-menu" density="compact" nav>
          <v-list-item
            :to="profileTo"
            prepend-icon="mdi-account-outline"
            :title="$t('teacher.actions.viewProfile')"
          />
        </v-list>
      </v-menu>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherLessonProgressMini from './TeacherLessonProgressMini.vue'
import { subscriptionStatusLabel } from '../../../utils/subscriptionStatus.js'
import { formatLessonRelativeDate } from '../../../utils/lessonWorkspaceDisplay.js'

const props = defineProps({
  student: { type: Object, required: true },
})

const profileTo = computed(() => ({
  name: 'teacher-student-profile',
  params: { studentId: props.student.student_id },
}))

const lastActivity = computed(() => formatLessonRelativeDate(props.student.last_activity_at))

const initials = computed(() => {
  const n = String(props.student.full_name || '').trim()
  if (!n) return t('teacher.labels.studentInitial')
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`
  return n.slice(0, 2)
})
</script>
