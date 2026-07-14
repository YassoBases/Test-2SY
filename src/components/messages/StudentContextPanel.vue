<template>
  <aside class="student-context-panel pa-4 chat-scroll">
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-3" />
    <button
      v-else-if="ctx?.student"
      type="button"
      class="context-card context-card--clickable"
      @click="$emit('open-profile', ctx.student.student_id)"
    >
      <div class="text-overline text-medium-emphasis mb-2">{{ t('messages.contextPanel.title') }}</div>
      <div class="d-flex align-center gap-2 mb-3">
        <ParticipantAvatar :name="ctx.student.full_name" role="student" :size="44" />
        <div class="text-start min-w-0">
          <div class="text-h6 font-weight-bold text-truncate">{{ ctx.student.full_name }}</div>
          <div
            v-if="ctx.course_context_label"
            class="text-caption text-primary text-truncate"
          >
            {{ ctx.course_context_label }}
          </div>
          <span v-else class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.clickForProfile') }}</span>
        </div>
        <v-icon size="20" class="ms-auto">mdi-chevron-left</v-icon>
      </div>

      <v-row dense class="mb-3">
        <v-col cols="6">
          <div class="metric-card">
            <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.grade') }}</div>
            <div class="text-body-1 font-weight-bold">{{ ctx.student.grade ?? '—' }}</div>
          </div>
        </v-col>
        <v-col cols="6">
          <div class="metric-card">
            <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.status') }}</div>
            <v-chip size="x-small" :color="ctx.student.is_active ? 'success' : 'warning'" variant="tonal">
              {{ ctx.student.status }}
            </v-chip>
          </div>
        </v-col>
        <v-col cols="6">
          <div class="metric-card">
            <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.completion') }}</div>
            <div class="text-body-1 font-weight-bold">{{ ctx.student.completion_percent }}%</div>
          </div>
        </v-col>
        <v-col cols="6">
          <div class="metric-card">
            <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.quizAverage') }}</div>
            <div class="text-body-1 font-weight-bold">{{ ctx.student.average_quiz_percent }}%</div>
          </div>
        </v-col>
        <v-col cols="6">
          <div class="metric-card">
            <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.streak') }}</div>
            <div class="text-body-1 font-weight-bold">{{ t('messages.contextPanel.streakDays', { count: ctx.student.current_streak }) }}</div>
          </div>
        </v-col>
        <v-col cols="12">
          <div class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.lastActivity') }}</div>
          <div class="text-body-2">{{ formatDate(ctx.student.last_activity_at) }}</div>
        </v-col>
      </v-row>

      <div v-if="ctx.student.enrolled_subjects?.length" class="mb-4">
        <div class="text-caption text-medium-emphasis mb-1">{{ t('messages.contextPanel.subjects') }}</div>
        <div class="d-flex flex-wrap gap-1">
          <v-chip v-for="s in ctx.student.enrolled_subjects" :key="s" size="x-small" variant="tonal">
            {{ s }}
          </v-chip>
        </div>
      </div>

      <div v-if="ctx.snapshot" class="snapshot-block">
        <div class="text-subtitle-2 font-weight-bold mb-2">{{ t('messages.contextPanel.quickSnapshot') }}</div>
        <SnapshotRow v-if="ctx.snapshot.latest_quiz" icon="mdi-clipboard-check" :label="t('messages.context.latestQuiz')" :item="ctx.snapshot.latest_quiz" />
        <SnapshotRow v-if="ctx.snapshot.latest_lesson_activity" icon="mdi-book-open-page-variant" :label="t('messages.context.latestLesson')" :item="ctx.snapshot.latest_lesson_activity" />
        <SnapshotRow v-if="ctx.snapshot.latest_teacher_note" icon="mdi-note-text" :label="t('messages.context.teacherNote')" :item="ctx.snapshot.latest_teacher_note" />
        <SnapshotRow v-if="ctx.snapshot.latest_parent_interaction" icon="mdi-account-child" :label="t('messages.context.parentInteraction')" :item="ctx.snapshot.latest_parent_interaction" />
      </div>
    </button>
    <template v-else-if="ctx?.parent">
      <div class="text-overline text-medium-emphasis mb-2">{{ t('messages.contextPanel.parentSection') }}</div>
      <div class="text-h6 font-weight-bold">{{ ctx.parent.parent_name }}</div>
      <p class="text-body-2 mt-2">
        {{ t('messages.contextPanel.linkedToStudent') }} <strong>{{ ctx.parent.linked_student_name }}</strong>
      </p>
      <p class="text-caption text-medium-emphasis">{{ t('messages.contextPanel.grade') }}: {{ ctx.parent.student_grade ?? '—' }}</p>
    </template>
    <p v-else class="text-caption text-medium-emphasis text-center py-6">{{ t('messages.contextPanel.noContext') }}</p>
  </aside>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import SnapshotRow from './SnapshotRow.vue'

defineProps({
  ctx: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

defineEmits(['open-profile'])

const { t, locale } = useI18n()

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat(locale.value === 'ar' ? 'ar-SY' : 'en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>

<style scoped>
.student-context-panel {
  height: 100%;
  overflow-y: auto;
}

.metric-card {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(124, 108, 240, 0.08);
  border: 1px solid rgba(124, 108, 240, 0.12);
  min-height: 52px;
}

.snapshot-block {
  padding-top: 8px;
  border-top: 1px solid rgba(124, 108, 240, 0.12);
}

.context-card {
  width: 100%;
  text-align: right;
  border: none;
  background: transparent;
  color: inherit;
  padding: 0;
}

.context-card--clickable {
  cursor: pointer;
  border-radius: 12px;
  padding: 4px;
  margin: -4px;
  transition: background 0.2s;
}

.context-card--clickable:hover {
  background: rgba(124, 108, 240, 0.12);
}
</style>
