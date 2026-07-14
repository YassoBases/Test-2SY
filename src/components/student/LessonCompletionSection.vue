<template>
  <v-card class="glass-card lesson-completion-section pa-5 mt-5" variant="flat">
    <div class="d-flex align-center gap-2 mb-4 flex-wrap">
      <v-icon color="secondary">mdi-book-check-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('student.lesson.completion.title') }}</h3>
      <v-chip v-if="progress?.completion_type === 'verified'" size="x-small" color="success" variant="flat" class="ms-auto">
        {{ t('student.lesson.completion.verified') }}
      </v-chip>
    </div>

    <v-skeleton-loader v-if="loading" type="list-item-three-line, button" />

    <template v-else-if="progress">
      <p class="text-body-2 text-medium-emphasis mb-4">{{ t('student.lesson.completion.instructions') }}</p>

      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-subtitle-2 font-weight-bold">{{ t('student.lesson.completion.overallProgress') }}</span>
        <span class="text-caption">{{ progress.completion_percent }}%</span>
      </div>
      <v-progress-linear
        :model-value="progress.completion_percent"
        color="secondary"
        height="8"
        rounded
        class="mb-4"
      />

      <v-list density="compact" class="bg-transparent requirement-list mb-4">
        <v-list-item
          v-for="item in displayChecklist"
          :key="item.key"
          rounded="lg"
          class="requirement-list__item mb-1"
        >
          <template #prepend>
            <v-icon :color="item.met ? 'success' : 'default'" size="20">
              {{ item.met ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
          </template>
          <v-list-item-title class="text-body-2">{{ item.label }}</v-list-item-title>
          <v-list-item-subtitle v-if="item.detail" class="text-caption">{{ item.detail }}</v-list-item-subtitle>
        </v-list-item>
      </v-list>

      <v-alert
        v-if="progress.is_completed"
        type="success"
        variant="tonal"
        class="mb-0"
        prominent
      >
        <div class="d-flex align-center gap-2">
          <v-icon>mdi-check-decagram</v-icon>
          <div>
            <strong>{{ t('student.lesson.completion.done') }}</strong>
            <div v-if="progress.completed_at" class="text-caption mt-1">
              {{ t('student.lesson.completion.completedAt', { date: formatDate(progress.completed_at) }) }}
            </div>
          </div>
        </div>
      </v-alert>

      <v-btn
        v-else
        color="primary"
        size="large"
        rounded="lg"
        class="btn-glow"
        block
        :loading="verifying"
        @click="$emit('verify')"
      >
        {{ t('student.lesson.completion.finishCta') }}
      </v-btn>
    </template>

    <v-alert v-else-if="loadError" type="warning" variant="tonal" class="mb-0">
      {{ loadError }}
      <v-btn size="small" variant="text" class="mt-2" @click="$emit('retry')">{{ t('student.lesson.completion.retryCta') }}</v-btn>
    </v-alert>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  progress: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  verifying: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
})

defineEmits(['verify', 'retry'])

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('ar-SY', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch {
    return iso
  }
}

const displayChecklist = computed(() => {
  const p = props.progress
  if (!p) return []

  if (p.checklist?.length) {
    return p.checklist.map((item) => ({
      ...item,
      detail: detailForKey(item.key, p),
    }))
  }

  const reqs = p.requirements || {}
  const items = []
  if (reqs.requires_video) {
    items.push({
      key: 'video',
      label: t('student.lesson.completion.requirements.videoFull'),
      met: reqs.video_met,
      detail: `${Math.round(p.video_progress_percent || 0)}%`,
    })
  }
  if (reqs.requires_pdf) {
    items.push({
      key: 'pdf',
      label: t('student.lesson.completion.requirements.pdfFull'),
      met: reqs.pdf_met,
      detail: `${Math.round(p.pdf_progress_percent || 0)}%`,
    })
  }
  if (reqs.requires_quiz) {
    items.push({
      key: 'quiz_submit',
      label: t('student.lesson.completion.requirements.quizAll'),
      met: reqs.quiz_submitted_met,
      detail: p.quiz_submitted
        ? t('student.lesson.completion.quizSubmitted.yes')
        : t('student.lesson.completion.quizSubmitted.no'),
    })
    items.push({
      key: 'quiz_score',
      label: t('student.lesson.completion.requirements.quizPerfect'),
      met: reqs.quiz_score_met,
      detail: `${Math.round(p.quiz_score_percent || 0)}%`,
    })
  }
  if (!items.length) {
    items.push({
      key: 'engage',
      label: t('student.lesson.completion.requirements.engage'),
      met: (p.completion_percent || 0) > 0,
      detail: `${p.completion_percent || 0}%`,
    })
  }
  return items
})

function detailForKey(key, p) {
  if (key === 'video') return `${Math.round(p.video_progress_percent || 0)}%`
  if (key === 'pdf') return `${Math.round(p.pdf_progress_percent || 0)}%`
  if (key === 'quiz_submit') {
    return p.quiz_submitted
      ? t('student.lesson.completion.quizSubmitted.yes')
      : t('student.lesson.completion.quizSubmitted.no')
  }
  if (key === 'quiz_score') return `${Math.round(p.quiz_score_percent || 0)}%`
  return ''
}
</script>

<style scoped>
.lesson-completion-section {
  border: 1px solid var(--em-border);
}

.requirement-list__item {
  border: 1px solid var(--em-border);
  background: var(--em-surface-secondary);
}
</style>
