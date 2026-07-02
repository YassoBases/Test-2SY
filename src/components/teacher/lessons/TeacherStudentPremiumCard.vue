<template>
  <article class="student-premium-card">
    <div class="student-premium-card__menu">
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
            class="student-premium-card__menu-btn"
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

    <div class="student-premium-card__identity">
      <span class="student-premium-card__avatar" aria-hidden="true">{{ initials }}</span>
      <div class="student-premium-card__identity-text">
        <router-link :to="profileTo" class="student-premium-card__name">
          {{ student.full_name }}
        </router-link>
        <span
          class="student-premium-card__status"
          :class="`student-premium-card__status--${student.subscription_status}`"
        >
          {{ subscriptionStatusLabel(student.subscription_status) }}
        </span>
        <p v-if="lastActivity" class="student-premium-card__activity">
          {{ $t('teacher.labels.lastActivityAt', { date: lastActivity }) }}
        </p>
      </div>
    </div>

    <div class="student-premium-card__stats">
      <div class="student-premium-card__stat">
        <span class="student-premium-card__stat-label">{{ $t('teacher.lessons.lessonProgress') }}</span>
        <div class="student-premium-card__progress-track" aria-hidden="true">
          <div
            class="student-premium-card__progress-fill"
            :style="{ width: `${safeProgress}%` }"
          />
        </div>
        <span class="student-premium-card__stat-value">{{ safeProgress }}%</span>
      </div>

      <div class="student-premium-card__stat student-premium-card__stat--inline">
        <span class="student-premium-card__stat-label">{{ $t('teacher.labels.quiz') }}</span>
        <span class="student-premium-card__stat-value">{{ student.avg_quiz_percent }}%</span>
      </div>

      <div class="student-premium-card__stat student-premium-card__stat--inline">
        <span class="student-premium-card__stat-label">{{ $t('teacher.lessons.documentedCompletion') }}</span>
        <span class="student-premium-card__stat-value">
          {{ student.verified_completions }}/{{ student.total_lessons }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

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

const safeProgress = computed(() =>
  Math.min(100, Math.max(0, Number(props.student.progress_percent) || 0)),
)

const initials = computed(() => {
  const n = String(props.student.full_name || '').trim()
  if (!n) return t('teacher.labels.studentInitial')
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`
  return n.slice(0, 2)
})
</script>
