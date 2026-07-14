<template>
  <v-card
    class="parent-lesson-card pa-3 pa-md-4 h-100"
    variant="flat"
    rounded="lg"
    role="button"
    tabindex="0"
    @click="$emit('open', lesson.lesson_id)"
    @keydown.enter="$emit('open', lesson.lesson_id)"
  >
    <div class="d-flex align-start gap-3">
      <div class="lesson-type-icon" :class="`lesson-type-icon--${lesson.status}`">
        <v-icon :icon="lesson.lesson_type_icon || 'mdi-book-open-page-variant-outline'" size="22" />
      </div>

      <div class="flex-grow-1 min-width-0">
        <div class="d-flex align-center justify-space-between gap-2 mb-1">
          <p class="text-body-2 font-weight-bold lesson-title mb-0">
            {{ lesson.lesson_title || t('parent.common.emDash') }}
          </p>
          <v-icon size="16" class="text-medium-emphasis flex-shrink-0">mdi-chevron-left</v-icon>
        </div>

        <div class="d-flex flex-wrap align-center gap-1 mb-2">
          <v-chip size="x-small" variant="tonal" :color="statusColor" class="font-weight-medium">
            {{ lesson.status_label }}
          </v-chip>
          <v-chip size="x-small" variant="outlined" color="secondary">
            {{ lesson.lesson_type_label || t('parent.lessons.progress.lessonFallback') }}
          </v-chip>
          <v-chip
            v-if="lesson.is_verified"
            size="x-small"
            color="success"
            variant="flat"
            prepend-icon="mdi-shield-check"
          >
            {{ t('parent.lessons.progress.verified') }}
          </v-chip>
        </div>

        <div class="d-flex align-center justify-space-between text-caption mb-1">
          <span class="text-medium-emphasis">{{ t('parent.lessons.progress.progressLabel') }}</span>
          <span class="font-weight-bold" :class="progressTextClass">{{ lesson.completion_percent ?? 0 }}%</span>
        </div>
        <v-progress-linear
          :model-value="lesson.completion_percent ?? 0"
          :color="progressBarColor"
          height="6"
          rounded
          class="mb-2"
        />

        <div class="lesson-meta text-caption text-medium-emphasis">
          <div v-if="lastActivityLabel" class="d-flex align-center gap-1 mb-1">
            <v-icon size="14">mdi-clock-outline</v-icon>
            <span>{{ t('parent.lessons.progress.lastActivity', { date: lastActivityLabel }) }}</span>
          </div>
          <div v-if="lesson.teacher_name" class="d-flex align-center gap-1">
            <v-icon size="14">mdi-account-tie</v-icon>
            <span>{{ lesson.teacher_name }}</span>
          </div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  lesson: { type: Object, required: true },
})

defineEmits(['open'])

const { t, locale } = useI18n()

const statusColor = computed(() => {
  if (props.lesson.status === 'completed') return 'success'
  if (props.lesson.status === 'in_progress') return 'warning'
  return 'default'
})

const progressBarColor = computed(() => {
  if (props.lesson.status === 'completed') return 'success'
  if (props.lesson.status === 'in_progress') return 'warning'
  return 'primary'
})

const progressTextClass = computed(() => {
  if (props.lesson.status === 'completed') return 'text-success'
  if (props.lesson.status === 'in_progress') return 'text-warning'
  return ''
})

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

const lastActivityLabel = computed(() => {
  const iso = props.lesson.last_activity_at || props.lesson.completed_at
  if (!iso) return null
  try {
    return new Intl.DateTimeFormat(dateLocale(), {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(new Date(iso))
  } catch {
    return iso
  }
})
</script>

<style scoped>
.parent-lesson-card {
  cursor: pointer;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.15s ease;
}

.parent-lesson-card:hover {
  border-color: rgba(34, 211, 238, 0.4);
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.parent-lesson-card:focus-visible {
  outline: 2px solid rgba(124, 108, 240, 0.6);
  outline-offset: 2px;
}

.lesson-type-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 108, 240, 0.12);
  color: rgb(var(--v-theme-primary));
}

.lesson-type-icon--completed {
  background: rgba(var(--v-theme-success), 0.15);
  color: rgb(var(--v-theme-success));
}

.lesson-type-icon--in_progress {
  background: rgba(var(--v-theme-warning), 0.15);
  color: rgb(var(--v-theme-warning));
}

.lesson-title {
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.min-width-0 {
  min-width: 0;
}
</style>
