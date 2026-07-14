<template>
  <button
    type="button"
    class="parent-teacher-item"
    :class="{ 'parent-teacher-item--unread': contact.unread_count > 0, 'parent-teacher-item--active': active }"
    @click="$emit('select', contact)"
  >
    <TeacherAvatar
      :name="contact.teacher_name"
      :image-url="contact.teacher_image_url"
      :size="48"
    />
    <div class="parent-teacher-item__body min-w-0">
      <div class="d-flex justify-space-between align-start gap-2">
        <div class="min-w-0">
          <div class="text-subtitle-2 font-weight-bold text-truncate">
            {{ contact.teacher_name }}
          </div>
          <div class="text-caption text-primary text-truncate">{{ contact.subject_name }}</div>
          <div class="text-caption text-medium-emphasis text-truncate">
            {{ t('parent.messaging.studentColon', { name: contact.student_name }) }}
          </div>
        </div>
        <span v-if="contact.last_message_at" class="text-caption text-medium-emphasis flex-shrink-0">
          {{ listTime }}
        </span>
      </div>
      <div class="text-caption text-truncate mt-1 parent-teacher-item__preview">
        {{ contact.last_message_preview || t('parent.messaging.startConversation') }}
      </div>
    </div>
    <div v-if="contact.unread_count > 0" class="parent-teacher-item__badge">
      {{ contact.unread_count > 99 ? '99+' : contact.unread_count }}
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import { formatListTime } from '../../utils/messagingUi.js'

const props = defineProps({
  contact: { type: Object, required: true },
  active: { type: Boolean, default: false },
})

defineEmits(['select'])

const { t } = useI18n()

const listTime = computed(() => formatListTime(props.contact.last_message_at))
</script>

<style scoped>
.parent-teacher-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: inherit;
  text-align: right;
  border-bottom: 1px solid rgba(124, 108, 240, 0.08);
  transition: background 0.2s ease;
}
.parent-teacher-item:hover {
  background: rgba(124, 108, 240, 0.1);
}
.parent-teacher-item--active {
  background: rgba(124, 108, 240, 0.2);
  border-inline-end: 3px solid var(--em-cyan);
}
.parent-teacher-item--unread .text-subtitle-2 {
  font-weight: 800;
}
.parent-teacher-item__preview {
  color: var(--em-text-muted);
}
.parent-teacher-item--unread .parent-teacher-item__preview {
  color: #e8ecf4;
  font-weight: 500;
}
.parent-teacher-item__badge {
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 11px;
  background: linear-gradient(135deg, #f87171, #ef4444);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.min-w-0 {
  min-width: 0;
}
</style>
