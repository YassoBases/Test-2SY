<template>
  <div ref="rootRef" class="lesson-assistant-panel glass-card">
    <div class="lesson-assistant-panel__teacher pa-3 pa-md-4">
      <TeacherAvatar
        :name="teacherName"
        :image-url="teacherImageUrl"
        :size="40"
        class="flex-shrink-0"
      />
      <div class="lesson-assistant-panel__identity flex-grow-1 min-width-0">
        <p class="lesson-assistant-panel__name text-subtitle-2 font-weight-bold mb-0 text-truncate">
          {{ teacherName }}
        </p>
        <p class="lesson-assistant-panel__tagline text-caption text-medium-emphasis mb-0">
          {{ t('student.lesson.assistant.subtitle') }}
        </p>
      </div>
      <v-tooltip :text="t('student.chat.clear.tooltip')" location="bottom">
        <template #activator="{ props: tooltipProps }">
          <v-btn
            v-bind="tooltipProps"
            icon="mdi-broom"
            size="small"
            variant="text"
            color="medium-emphasis"
            :disabled="clearDisabled || isTyping"
            :loading="clearLoading"
            :aria-label="t('student.chat.clear.aria')"
            @click="$emit('clear')"
          />
        </template>
      </v-tooltip>
    </div>
    <div class="lesson-assistant-panel__body">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'

const { t } = useI18n()

defineProps({
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
  clearDisabled: { type: Boolean, default: false },
  clearLoading: { type: Boolean, default: false },
  isTyping: { type: Boolean, default: false },
})

defineEmits(['clear'])

const rootRef = ref(null)

defineExpose({
  getRootElement: () => rootRef.value,
})
</script>
