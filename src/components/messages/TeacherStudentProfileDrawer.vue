<template>
  <Transition name="wa-info-slide">
    <div
      v-if="modelValue"
      class="wa-student-drawer-layer"
      role="dialog"
      aria-modal="true"
      :aria-label="t('messages.studentDrawer.title')"
    >
      <button type="button" class="wa-info-backdrop" :aria-label="t('common.close')" @click="close" />
      <aside class="wa-student-drawer-panel chat-scroll">
        <div class="wa-student-drawer-panel__head">
          <h3 class="wa-student-drawer-panel__title">{{ t('messages.studentDrawer.title') }}</h3>
          <v-btn icon size="small" variant="text" :aria-label="t('common.close')" @click="close">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-3" />

        <template v-else-if="profile">
          <div class="wa-student-drawer-profile">
            <TeacherAvatar :name="profile.info.full_name" :size="64" />
            <div class="min-w-0">
              <div class="text-h6 font-weight-bold text-truncate">{{ profile.info.full_name }}</div>
              <div v-if="profile.info.email" class="text-caption text-medium-emphasis text-truncate">
                {{ profile.info.email }}
              </div>
              <v-chip
                size="x-small"
                :color="profile.info.account_status === 'active' ? 'success' : 'warning'"
                variant="tonal"
                class="mt-1"
              >
                {{ profile.info.account_status === 'active' ? t('messages.studentDrawer.active') : t('messages.studentDrawer.expired') }}
              </v-chip>
            </div>
          </div>

          <p v-if="profile.analytics_scope_label" class="text-caption text-medium-emphasis mb-3">
            {{ profile.analytics_scope_label }}
          </p>

          <div class="wa-student-drawer-metrics">
            <div class="wa-student-drawer-metric">
              <span class="wa-student-drawer-metric__label">{{ t('messages.metrics.lessonCompletion') }}</span>
              <span class="wa-student-drawer-metric__value" dir="ltr">{{ profile.analytics.completion_percent }}%</span>
            </div>
            <div class="wa-student-drawer-metric">
              <span class="wa-student-drawer-metric__label">{{ t('messages.metrics.quizAverage') }}</span>
              <span class="wa-student-drawer-metric__value" dir="ltr">{{ profile.analytics.average_score_percent }}%</span>
            </div>
            <div class="wa-student-drawer-metric">
              <span class="wa-student-drawer-metric__label">{{ t('messages.metrics.lessonsCompleted') }}</span>
              <span class="wa-student-drawer-metric__value" dir="ltr">{{ profile.learning.lessons_completed }}</span>
            </div>
            <div v-if="profile.analytics.last_active_date" class="wa-student-drawer-metric">
              <span class="wa-student-drawer-metric__label">{{ t('messages.metrics.lastActivity') }}</span>
              <span class="wa-student-drawer-metric__value">{{ formatDate(profile.analytics.last_active_date) }}</span>
            </div>
          </div>

          <section v-if="profile.quiz_analytics" class="wa-student-drawer-section">
            <h4 class="wa-student-drawer-section__title">{{ t('messages.studentDrawer.quizPerformance') }}</h4>
            <div class="wa-student-drawer-stats-row">
              <div>
                <div class="text-body-1 font-weight-bold">{{ profile.quiz_analytics.total_completed }}</div>
                <div class="text-caption text-medium-emphasis">{{ t('messages.studentDrawer.completed') }}</div>
              </div>
              <div>
                <div class="text-body-1 font-weight-bold" dir="ltr">{{ profile.quiz_analytics.average_score_percent }}%</div>
                <div class="text-caption text-medium-emphasis">{{ t('messages.studentDrawer.average') }}</div>
              </div>
              <div>
                <div class="text-body-1 font-weight-bold" dir="ltr">{{ profile.quiz_analytics.best_score_percent }}%</div>
                <div class="text-caption text-medium-emphasis">{{ t('messages.studentDrawer.best') }}</div>
              </div>
            </div>
          </section>

          <section v-if="profile.learning" class="wa-student-drawer-section">
            <h4 class="wa-student-drawer-section__title">{{ t('messages.studentDrawer.learningProgress') }}</h4>
            <div class="wa-student-drawer-stats-row">
              <div>
                <div class="text-body-1 font-weight-bold">{{ profile.learning.active_courses }}</div>
                <div class="text-caption text-medium-emphasis">{{ t('messages.studentDrawer.activeSubjects') }}</div>
              </div>
              <div>
                <div class="text-body-1 font-weight-bold">{{ profile.learning.lessons_remaining }}</div>
                <div class="text-caption text-medium-emphasis">{{ t('messages.studentDrawer.lessonsRemaining') }}</div>
              </div>
            </div>
          </section>

          <section v-if="profile.activity_timeline?.length" class="wa-student-drawer-section">
            <h4 class="wa-student-drawer-section__title">{{ t('messages.studentDrawer.recentActivity') }}</h4>
            <v-timeline side="end" density="compact" truncate-line="both">
              <v-timeline-item
                v-for="event in profile.activity_timeline.slice(0, 5)"
                :key="event.id"
                size="x-small"
                dot-color="primary"
              >
                <div class="text-body-2 font-weight-medium">{{ event.title }}</div>
                <div v-if="event.description" class="text-caption text-medium-emphasis">{{ event.description }}</div>
                <div class="text-caption text-medium-emphasis">{{ formatDate(event.occurred_at) }}</div>
              </v-timeline-item>
            </v-timeline>
          </section>

          <div class="wa-student-drawer-actions">
            <v-btn
              block
              variant="tonal"
              color="primary"
              rounded="lg"
              prepend-icon="mdi-bell-outline"
              @click="$emit('send-notification')"
            >
              {{ t('messages.studentDrawer.sendNotification') }}
            </v-btn>
            <v-btn
              block
              variant="tonal"
              rounded="lg"
              prepend-icon="mdi-clipboard-text-outline"
              @click="$emit('view-quizzes', studentId)"
            >
              {{ t('messages.studentDrawer.viewQuizzes') }}
            </v-btn>
            <v-btn
              v-if="courseId"
              block
              variant="tonal"
              rounded="lg"
              prepend-icon="mdi-school-outline"
              @click="$emit('open-class', courseId)"
            >
              {{ t('messages.studentDrawer.viewClass') }}
            </v-btn>
            <v-btn
              block
              variant="flat"
              color="primary"
              rounded="lg"
              prepend-icon="mdi-open-in-new"
              @click="$emit('open-full-profile', studentId)"
            >
              {{ t('messages.studentDrawer.openFullProfile') }}
            </v-btn>
          </div>
        </template>

        <p v-else class="text-caption text-medium-emphasis text-center py-8">
          {{ t('messages.studentDrawer.loadFailed') }}
        </p>
      </aside>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import { fetchTeacherStudentProfile } from '../../api/teacherStudents.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  studentId: { type: Number, default: null },
  courseId: { type: Number, default: null },
  cachedProfile: { type: Object, default: null },
})

const emit = defineEmits([
  'update:modelValue',
  'send-notification',
  'view-quizzes',
  'open-class',
  'open-full-profile',
])

const { t, locale } = useI18n()

const loading = ref(false)
const profile = ref(null)

watch(
  () => [props.modelValue, props.studentId, props.cachedProfile],
  async ([open, studentId]) => {
    if (!open || !studentId) {
      profile.value = null
      return
    }
    if (props.cachedProfile?.info?.full_name) {
      profile.value = props.cachedProfile
      loading.value = false
      return
    }
    loading.value = true
    try {
      profile.value = await fetchTeacherStudentProfile(studentId)
    } catch {
      profile.value = null
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

function close() {
  emit('update:modelValue', false)
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat(locale.value === 'ar' ? 'ar-SY' : 'en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>
