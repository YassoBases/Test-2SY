<template>
  <div class="teacher-contact-card pa-4">
    <div class="text-overline text-medium-emphasis mb-2">{{ t('student.teacherContact.label') }}</div>
    <div class="d-flex align-center gap-3 mb-3">
      <TeacherAvatar :name="course.teacher_name" :image-url="teacherImageUrl" :size="52" />
      <div class="min-width-0 flex-grow-1">
        <div class="text-subtitle-1 font-weight-bold text-truncate">{{ course.teacher_name }}</div>
        <div class="text-caption text-medium-emphasis text-truncate">{{ course.subject_name }}</div>
        <v-chip size="x-small" color="success" variant="tonal" class="mt-1">
          {{ statusLabel }}
        </v-chip>
      </div>
    </div>

    <v-switch
      v-if="canContact && course.has_linked_parent"
      v-model="includeParentLocal"
      density="compact"
      hide-details
      color="primary"
      class="mb-2"
      :label="t('student.teacherContact.includeParent')"
    />

    <div class="d-flex flex-column gap-2">
      <v-tooltip
        v-if="!canContact"
        location="top"
        :text="t('student.teacherContact.subscribeTooltip')"
      >
        <template #activator="{ props: tipProps }">
          <span v-bind="tipProps" class="d-block w-100">
            <v-btn
              block
              color="primary"
              variant="tonal"
              rounded="lg"
              prepend-icon="mdi-message-text"
              disabled
            >
              {{ t('student.teacherContact.message') }}
            </v-btn>
          </span>
        </template>
      </v-tooltip>
      <v-btn
        v-else
        block
        color="primary"
        variant="tonal"
        rounded="lg"
        prepend-icon="mdi-message-text"
        :loading="messaging"
        @click="$emit('message-teacher', { includeParent: includeParentLocal })"
      >
        {{ t('student.teacherContact.message') }}
      </v-btn>
      <v-btn
        block
        variant="outlined"
        rounded="lg"
        prepend-icon="mdi-account-school"
        @click="$emit('view-profile')"
      >
        {{ t('student.teacherContact.viewProfile') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import { teacherImageFromEntity } from '../../utils/teacherAvatar.js'

const props = defineProps({
  course: { type: Object, required: true },
  messaging: { type: Boolean, default: false },
  canContact: { type: Boolean, default: true },
})

const { t } = useI18n()

defineEmits(['message-teacher', 'view-profile'])

const includeParentLocal = ref(false)
const teacherImageUrl = computed(() => teacherImageFromEntity(props.course))

const statusLabel = computed(() => t('student.teacherContact.status'))
</script>

<style scoped>
.teacher-contact-card {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.min-width-0 {
  min-width: 0;
}
</style>
