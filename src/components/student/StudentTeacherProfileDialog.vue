<template>
  <v-dialog :model-value="modelValue" max-width="640" scrollable @update:model-value="$emit('update:modelValue', $event)">
    <v-card v-if="profile" rounded="xl" class="glass-card">
      <v-card-title class="d-flex align-center gap-3 pa-4">
        <TeacherAvatar :name="profile.full_name" :image-url="profile.image_url" :size="56" />
        <div class="min-width-0">
          <div class="text-h6 font-weight-bold text-truncate">{{ profile.full_name }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ t('student.teacherProfile.subtitle', { subject: profile.subject_name, grade: profile.grade }) }}
          </div>
        </div>
        <v-btn icon variant="text" class="ms-auto" @click="$emit('update:modelValue', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text class="pa-4">
        <div v-if="profile.rating" class="d-flex align-center gap-2 mb-3">
          <v-icon color="amber" size="20">mdi-star</v-icon>
          <span class="text-body-2">{{ profile.rating.toFixed(1) }}</span>
          <span v-if="profile.student_count" class="text-caption text-medium-emphasis">
            {{ t('student.teacherProfile.studentCount', { n: profile.student_count }) }}
          </span>
        </div>

        <div v-if="profile.bio" class="mb-4">
          <div class="text-overline text-medium-emphasis mb-1">{{ t('student.teacherProfile.bio') }}</div>
          <p class="text-body-2">{{ profile.bio }}</p>
        </div>

        <TeacherPortfolioDisplay :profile="profile" />

        <div v-if="profile.courses?.length" class="mt-4">
          <div class="text-overline text-medium-emphasis mb-2">{{ t('student.teacherProfile.courses') }}</div>
          <v-chip
            v-for="title in profile.courses"
            :key="title"
            size="small"
            variant="tonal"
            class="me-1 mb-1"
          >
            {{ title }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>
    <v-card v-else-if="loading" rounded="xl" class="pa-8 text-center">
      <v-progress-circular indeterminate color="primary" />
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import TeacherPortfolioDisplay from '../teacher/TeacherPortfolioDisplay.vue'

const { t } = useI18n()

defineProps({
  modelValue: { type: Boolean, default: false },
  profile: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.min-width-0 {
  min-width: 0;
}
</style>
