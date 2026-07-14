<template>
  <v-dialog :model-value="modelValue" max-width="480" @update:model-value="$emit('update:modelValue', $event)">
    <v-card class="glass-card pa-5" variant="flat">
      <div class="d-flex align-center justify-space-between mb-4">
        <h3 class="text-h6 font-weight-bold">{{ detail?.lesson_title || t('parent.lessons.detail.dialogTitle') }}</h3>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </div>

      <LoadingState v-if="loading" variant="inline" :label="t('parent.lessons.detail.dialogLoading')" />

      <v-alert v-else-if="error" type="error" variant="tonal" density="compact">{{ error }}</v-alert>

      <template v-else-if="detail">
        <v-list density="compact" class="bg-transparent">
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">{{ t('parent.lessons.detail.videoProgress') }}</v-list-item-title>
            <v-list-item-subtitle>{{ detail.video_progress_percent }}%</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">{{ t('parent.lessons.detail.pdfProgress') }}</v-list-item-title>
            <v-list-item-subtitle>{{ detail.pdf_progress_percent }}%</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">{{ t('parent.lessons.detail.quizScore') }}</v-list-item-title>
            <v-list-item-subtitle>{{ detail.quiz_score_percent }}%</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">{{ t('parent.lessons.detail.completionStatus') }}</v-list-item-title>
            <v-list-item-subtitle>{{ detail.verification_status_label }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="detail.completed_at">
            <v-list-item-title class="text-caption text-medium-emphasis">{{ t('parent.lessons.detail.completionDate') }}</v-list-item-title>
            <v-list-item-subtitle>{{ formatDate(detail.completed_at) }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import { fetchParentLessonDetail } from '../../api/parent.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  lessonId: { type: Number, default: null },
  studentId: { type: Number, default: null },
})

defineEmits(['update:modelValue'])

const { t, locale } = useI18n()

const loading = ref(false)
const error = ref('')
const detail = ref(null)

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString(dateLocale(), {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return iso
  }
}

watch(
  () => [props.modelValue, props.lessonId, props.studentId],
  async ([open, lessonId]) => {
    if (!open || !lessonId) return
    loading.value = true
    error.value = ''
    detail.value = null
    try {
      detail.value = await fetchParentLessonDetail(lessonId, props.studentId)
    } catch (e) {
      error.value = getErrorMessage(e, t('parent.errors.loadLessonDetail'))
    } finally {
      loading.value = false
    }
  },
)
</script>
