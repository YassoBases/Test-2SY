<template>
  <button
    type="button"
    class="conv-item"
    :class="{
      'conv-item--active': active,
      'conv-item--unread': conv.unread_count > 0,
    }"
    @click="$emit('select', conv.id)"
  >
    <ParticipantAvatar
      class="conv-item__avatar"
      :name="displayName"
      :role="primary?.role || 'student'"
      :image-url="avatarUrl"
      :size="52"
    />
    <div class="conv-item__body min-w-0">
      <div class="conv-item__top">
        <div class="conv-item__name-row min-w-0">
          <v-icon v-if="conv.is_pinned" size="14" color="primary" class="me-1 flex-shrink-0">mdi-pin</v-icon>
          <span class="conv-item__name text-truncate">{{ displayName }}</span>
          <v-chip
            v-if="roleBadgeLabel"
            size="x-small"
            :color="roleBadgeColor"
            variant="flat"
            class="ms-1 flex-shrink-0"
          >
            {{ roleBadgeLabel }}
          </v-chip>
          <span v-if="parentRelationship" class="conv-item__relationship ms-1 flex-shrink-0">
            {{ parentRelationship }}
          </span>
        </div>
        <span class="conv-item__time flex-shrink-0">{{ listTime }}</span>
      </div>
      <div v-if="conv.course_context_label" class="conv-item__course text-truncate">
        {{ conv.course_context_label }}
      </div>
      <div class="conv-item__preview text-truncate">
        {{ conv.last_message_preview || t('messages.noMessagesYet') }}
      </div>
    </div>
    <div v-if="conv.unread_count > 0" class="conv-item__unread-badge">
      {{ conv.unread_count > 99 ? '99+' : conv.unread_count }}
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import {
  formatListTime,
  parentRelationshipFromCache,
  primaryOtherParticipant,
  roleChipColor,
  ROLE_LABELS,
} from '../../utils/messagingUi.js'
import { relationshipLabelAr } from '../../utils/subscriptionStatus.js'
import { participantAvatarUrl } from '../../utils/teacherAvatar.js'

const props = defineProps({
  conv: { type: Object, required: true },
  viewerId: { type: Number, default: null },
  active: { type: Boolean, default: false },
  teacherAvatarUrl: { type: String, default: null },
  parentRelationships: { type: Object, default: () => ({}) },
})

defineEmits(['select'])

const { t } = useI18n()

const primary = computed(() => primaryOtherParticipant(props.conv, props.viewerId))

const kindLabel = computed(() => props.conv.conversation_kind_label || '')

const roleBadgeLabel = computed(() => {
  if (kindLabel.value) return kindLabel.value
  const role = primary.value?.role
  if (role === 'student') return t('messages.roles.student')
  if (role === 'parent') return t('messages.roles.parent')
  return roleLabel(role)
})

const roleBadgeColor = computed(() => {
  const threadType = props.conv.thread_type
  if (threadType === 'teacher_parent') return 'secondary'
  if (threadType === 'teacher_student') return 'cyan'
  const role = primary.value?.role
  if (role === 'parent') return 'secondary'
  if (role === 'student') return 'cyan'
  return roleChipColor(primary.value?.role)
})

const parentRelationship = computed(() => {
  if (props.conv.thread_type !== 'teacher_parent') return ''
  const p = primary.value
  if (!p || p.role !== 'parent') return ''
  const label = parentRelationshipFromCache(props.parentRelationships, p.user_id, props.conv.student_id)
  return label ? relationshipLabelAr(label) : ''
})

const displayName = computed(() => {
  const p = primary.value
  if (p) return p.display_name || p.name
  return props.conv.title || t('messages.conversation')
})

const avatarUrl = computed(() =>
  participantAvatarUrl(primary.value, props.teacherAvatarUrl, props.viewerId),
)

const listTime = computed(() =>
  formatListTime(props.conv.last_message_at || props.conv.created_at),
)

function roleLabel(role) {
  return ROLE_LABELS[role] || role
}
</script>

<style scoped>
.conv-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: right;
  padding: 12px 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: inherit;
  border-bottom: 1px solid var(--em-border-subtle);
  transition: background 0.22s ease;
}
.conv-item:hover {
  background: var(--em-surface-control);
}
.conv-item--active {
  background: rgba(99, 102, 241, 0.08);
  border-inline-end: 3px solid var(--em-primary);
}
.conv-item--unread .conv-item__name {
  font-weight: 800;
}
.conv-item--unread .conv-item__preview {
  color: var(--em-text);
  font-weight: 500;
}
.conv-item__relationship {
  font-size: 0.68rem;
  color: var(--em-text-muted);
  white-space: nowrap;
}
.conv-item__body {
  flex: 1;
}
.conv-item__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}
.conv-item__name-row {
  display: flex;
  align-items: center;
  min-width: 0;
}
.conv-item__name {
  font-size: 0.95rem;
  font-weight: 600;
}
.conv-item__time {
  font-size: 0.7rem;
  color: var(--em-text-muted);
  white-space: nowrap;
}
.conv-item__course {
  font-size: 0.72rem;
  color: var(--em-primary-deep);
  margin-bottom: 2px;
  line-height: 1.3;
}
.conv-item__preview {
  font-size: 0.8rem;
  color: var(--em-text-muted);
  line-height: 1.35;
}
.conv-item__unread-badge {
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
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.45);
  flex-shrink: 0;
}
</style>
