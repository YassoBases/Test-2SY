<template>
  <div class="teacher-helper-card pa-4 pa-md-5">
    <div class="teacher-helper-card__inner d-flex align-center flex-wrap gap-3 gap-md-4">
      <TeacherAvatar
        :name="teacherName"
        :image-url="teacherImageUrl"
        :size="56"
        class="teacher-helper-card__avatar flex-shrink-0"
      />
      <div class="teacher-helper-card__copy flex-grow-1 min-width-0">
        <p class="teacher-helper-card__name text-subtitle-1 font-weight-bold mb-1">
          {{ teacherName }}
        </p>
        <p class="teacher-helper-card__prompt text-body-2 text-medium-emphasis mb-0">
          {{ t('student.lesson.helper.prompt') }}
        </p>
        <p v-if="hint" class="teacher-helper-card__hint text-caption text-medium-emphasis mb-0 mt-1">
          {{ hint }}
        </p>
      </div>
      <v-btn
        color="secondary"
        variant="flat"
        size="large"
        rounded="lg"
        class="teacher-helper-card__cta flex-shrink-0"
        prepend-icon="mdi-message-text"
        :disabled="disabled"
        @click="$emit('ask')"
      >
        {{ t('student.lesson.helper.cta') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'

const { t } = useI18n()

defineProps({
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  disabled: { type: Boolean, default: false },
  hint: { type: String, default: '' },
})

defineEmits(['ask'])
</script>
