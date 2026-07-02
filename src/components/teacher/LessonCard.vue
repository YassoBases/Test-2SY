<template>
  <v-card class="glass-card eduspark-card-hover pa-5 lesson-card" variant="flat">
    <div class="d-flex align-center gap-3 mb-4">
      <v-avatar size="48" class="eduspark-gradient" rounded="lg">
        <v-icon color="white">mdi-file-pdf-box</v-icon>
      </v-avatar>
      <div class="flex-grow-1 min-width-0">
        <div class="text-subtitle-1 font-weight-bold text-truncate">{{ lesson.title }}</div>
        <div class="text-caption text-medium-emphasis">
          {{ lesson.subject }} · {{ lesson.grade }}
        </div>
      </div>
      <StatusBadge :status="lesson.status" />
    </div>

    <v-divider class="border-opacity-25 mb-4" />

    <div class="d-flex flex-wrap gap-3 text-caption text-medium-emphasis mb-4">
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-file-document</v-icon>
        {{ $t('teacher.labels.pagesCount', { count: lesson.pages }) }}
      </span>
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-account-group</v-icon>
        {{ $t('teacher.labels.studentCount', { count: lesson.students }) }}
      </span>
      <span>
        <v-icon size="14" class="me-1" color="secondary">mdi-calendar</v-icon>
        {{ lesson.uploadedAt }}
      </span>
    </div>

    <p v-if="lesson.preview" class="text-body-2 text-medium-emphasis lesson-preview mb-4">
      {{ lesson.preview }}
    </p>

    <div class="d-flex gap-2 flex-wrap">
      <v-btn
        v-if="lesson.status === 'processed'"
        class="btn-glow-outline flex-grow-1"
        size="small"
        prepend-icon="mdi-eye"
        :to="`/student/lesson/${lesson.id}`"
      >
        {{ $t('teacher.actions.studentPreview') }}
      </v-btn>
      <v-btn
        v-else-if="lesson.status === 'processing'"
        variant="tonal"
        color="warning"
        size="small"
        disabled
        class="flex-grow-1"
        prepend-icon="mdi-cog"
      >
        {{ $t('teacher.status.processingEllipsis') }}
      </v-btn>
      <v-btn
        v-else
        class="btn-glow-outline flex-grow-1"
        size="small"
        prepend-icon="mdi-pencil"
        :to="lesson.courseId ? `/teacher/grades/${lesson.courseId}` : '/teacher/grades'"
      >
        {{ $t('teacher.actions.completeUpload') }}
      </v-btn>
      <v-btn
        v-if="lesson.pdfUrl"
        icon
        size="small"
        variant="tonal"
        color="secondary"
        :href="lesson.pdfUrl"
        target="_blank"
        rel="noopener"
        :aria-label="$t('teacher.lessons.openPdfAria')"
      >
        <v-icon>mdi-file-eye</v-icon>
      </v-btn>
      <v-btn
        icon
        size="small"
        variant="tonal"
        color="error"
        :aria-label="$t('teacher.actions.deleteLesson')"
        @click="$emit('delete', lesson)"
      >
        <v-icon>mdi-delete-outline</v-icon>
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import StatusBadge from '../common/StatusBadge.vue'

defineProps({
  lesson: { type: Object, required: true },
})

defineEmits(['delete'])
</script>

<style scoped>
.lesson-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.lesson-card .d-flex.gap-2 {
  margin-top: auto;
}

.lesson-preview {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
}
</style>
