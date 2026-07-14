<template>
  <header class="teacher-quiz-detail__hero">
    <div class="teacher-quiz-detail__hero-main">
      <p class="teacher-quiz-detail__eyebrow">{{ displayEyebrow }}</p>
      <h1 class="teacher-quiz-detail__title">{{ title }}</h1>
      <p v-if="updatedLabel" class="teacher-quiz-detail__updated">{{ $t('teacher.labels.lastUpdated') }} {{ updatedLabel }}</p>
      <div class="teacher-quiz-detail__status" :class="statusClass">
        <span class="teacher-quiz-detail__status-dot" aria-hidden="true" />
        <span>{{ statusLabel }}</span>
      </div>
    </div>

    <div v-if="showActions" class="teacher-quiz-detail__hero-actions">
      <v-btn variant="tonal" size="small" rounded="lg" @click="$emit('edit')">
        <v-icon start size="16">mdi-pencil-outline</v-icon>
        {{ $t('common.edit') }}
      </v-btn>
      <v-btn variant="tonal" size="small" rounded="lg" @click="$emit('preview')">
        <v-icon start size="16">mdi-eye-outline</v-icon>
        {{ $t('teacher.actions.review') }}
      </v-btn>
      <v-btn
        variant="flat"
        size="small"
        rounded="lg"
        :color="isPublished ? 'warning' : 'secondary'"
        :loading="publishLoading"
        @click="$emit('toggle-publish')"
      >
        {{ isPublished ? $t('teacher.quizzes.unpublish') : $t('teacher.actions.publish') }}
      </v-btn>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  classLabel: { type: String, default: '' },
  updatedLabel: { type: String, default: '' },
  isPublished: { type: Boolean, default: false },
  needsReview: { type: Boolean, default: false },
  showActions: { type: Boolean, default: true },
  publishLoading: { type: Boolean, default: false },
})

defineEmits(['edit', 'preview', 'toggle-publish'])

const displayEyebrow = computed(() => props.eyebrow || t('teacher.quizzes.workspace'))

const statusClass = computed(() => {
  if (props.needsReview) return 'teacher-quiz-detail__status--review'
  return props.isPublished
    ? 'teacher-quiz-detail__status--published'
    : 'teacher-quiz-detail__status--draft'
})

const statusLabel = computed(() => {
  if (props.needsReview) return t('teacher.status.pendingReview')
  return props.isPublished ? t('teacher.status.published') : t('teacher.status.draft')
})
</script>
