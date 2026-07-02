<template>
  <v-card class="glass-card lesson-session-header" variant="flat">
    <div class="lesson-session-header__inner pa-4 pa-md-5">
      <div class="lesson-session-header__identity d-flex align-start gap-3 gap-md-4">
        <TeacherAvatar
          :name="teacherName"
          :image-url="teacherImageUrl"
          :size="avatarSize"
          class="lesson-session-header__avatar"
        />
        <div class="lesson-session-header__copy flex-grow-1 min-width-0">
          <p class="lesson-session-header__teacher text-subtitle-1 text-md-h6 font-weight-bold mb-1">
            {{ teacherName }}
          </p>
          <p v-if="subjectLine" class="lesson-session-header__meta text-caption text-medium-emphasis mb-2">
            {{ subjectLine }}
          </p>
          <h1 class="lesson-session-header__title text-h6 text-md-h5 font-weight-bold mb-2">
            {{ lessonTitle }}
          </h1>
          <v-chip
            v-if="lessonPosition"
            size="small"
            variant="tonal"
            color="secondary"
            class="lesson-session-header__position"
          >
            {{ lessonPosition }}
          </v-chip>
        </div>
        <v-btn
          v-if="pdfUrl"
          class="lesson-session-header__pdf d-none d-md-flex"
          color="secondary"
          variant="tonal"
          size="small"
          prepend-icon="mdi-file-pdf-box"
          :href="pdfUrl"
          target="_blank"
          rel="noopener"
        >
          {{ t('student.lesson.header.pdf') }}
        </v-btn>
      </div>

      <div class="lesson-session-header__progress mt-4 mt-md-5">
        <div class="d-flex align-center justify-space-between gap-3 mb-2">
          <span class="section-eyebrow mb-0">{{ t('student.lesson.header.sessionProgress') }}</span>
          <span class="lesson-session-header__percent text-caption font-weight-bold">
            {{ progressPercent }}%
          </span>
        </div>
        <AnimatedProgressBar
          :value="progressPercent"
          color="secondary"
          :height="8"
          class="lesson-session-header__bar"
        />
      </div>

      <div class="lesson-session-header__next mt-4">
        <div class="lesson-session-header__next-row d-flex align-center flex-wrap gap-3">
          <v-icon :icon="nextAction.icon" color="secondary" size="22" class="flex-shrink-0" />
          <div class="lesson-session-header__next-copy flex-grow-1 min-width-0">
            <span class="lesson-session-header__next-label">{{ nextAction.label || t('student.lesson.header.nextStep') }}</span>
            <strong class="lesson-session-header__next-text">{{ nextAction.text }}</strong>
          </div>
          <v-btn
            v-if="nextAction.cta"
            size="small"
            color="secondary"
            variant="flat"
            class="lesson-session-header__next-btn flex-shrink-0"
            :disabled="nextAction.disabled"
            :loading="nextAction.loading || actionLoading"
            @click="$emit('action', nextAction.action)"
          >
            {{ nextAction.cta }}
          </v-btn>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'
import AnimatedProgressBar from '../home/AnimatedProgressBar.vue'

const { t } = useI18n()

const props = defineProps({
  lessonTitle: { type: String, default: '' },
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  subject: { type: String, default: '' },
  grade: { type: String, default: '' },
  lessonPosition: { type: String, default: '' },
  progressPercent: { type: Number, default: 0 },
  nextAction: {
    type: Object,
    default: () => ({
      label: '',
      text: '',
      action: null,
      cta: '',
      icon: 'mdi-arrow-left-circle',
      disabled: false,
      loading: false,
    }),
  },
  pdfUrl: { type: String, default: null },
  actionLoading: { type: Boolean, default: false },
})

defineEmits(['action'])

const avatarSize = 72

const subjectLine = computed(() => {
  const parts = [props.subject, props.grade].filter(Boolean)
  return parts.join(' · ')
})
</script>
