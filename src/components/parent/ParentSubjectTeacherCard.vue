<template>
  <v-card class="glass-card subject-teacher-card pa-4 h-100" variant="flat">
    <div class="d-flex align-start gap-3 mb-3">
      <TeacherAvatar
        :name="item.teacher_name"
        :image-url="item.teacher_image_url"
        :size="52"
      />
      <div class="min-width-0 flex-grow-1">
        <div class="text-subtitle-1 font-weight-bold text-truncate">{{ item.subject_name }}</div>
        <div class="text-body-2 text-medium-emphasis text-truncate">{{ item.course_title }}</div>
        <div class="text-caption mt-1">
          <v-icon size="14" class="me-1">mdi-account-tie</v-icon>
          {{ item.teacher_name }}
        </div>
      </div>
      <v-chip
        v-if="item.enrolled"
        size="x-small"
        color="success"
        variant="tonal"
      >
        {{ t('parent.subjectsTeachers.enrolled') }}
      </v-chip>
      <v-chip
        v-else
        size="x-small"
        color="secondary"
        variant="tonal"
      >
        {{ t('parent.subjectsTeachers.availableChip') }}
      </v-chip>
    </div>

    <v-progress-linear
      v-if="item.enrolled && item.lesson_count > 0"
      :model-value="item.progress_percent"
      color="primary"
      height="6"
      rounded
      class="mb-3"
    />

    <div class="d-flex flex-wrap gap-2">
      <v-btn
        size="small"
        variant="tonal"
        color="primary"
        prepend-icon="mdi-account-details-outline"
        @click="$emit('view-profile', item)"
      >
        {{ t('parent.subjectsTeachers.teacherProfile') }}
      </v-btn>
      <v-btn
        v-if="item.enrolled"
        size="small"
        variant="tonal"
        color="secondary"
        prepend-icon="mdi-message-text-outline"
        :loading="contacting"
        @click="$emit('contact', item)"
      >
        {{ t('parent.subjectsTeachers.contact') }}
        <v-badge
          v-if="item.unread_count"
          :content="item.unread_count"
          color="error"
          inline
          class="ms-1"
        />
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'

defineProps({
  item: { type: Object, required: true },
  contacting: { type: Boolean, default: false },
})

defineEmits(['view-profile', 'contact'])

const { t } = useI18n()
</script>

<style scoped>
.subject-teacher-card {
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.min-width-0 {
  min-width: 0;
}
</style>
