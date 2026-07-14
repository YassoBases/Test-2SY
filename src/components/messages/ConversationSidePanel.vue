<template>
  <div class="wa-side-panel chat-scroll">
    <StudentContextPanel
      v-if="viewerRole === 'teacher'"
      :ctx="teacherCtx"
      :loading="loading"
      @open-profile="$emit('open-profile', $event)"
    />
    <div v-else class="wa-side-panel__body pa-4">
      <template v-if="activeThread">
        <div
          v-for="p in otherParticipants"
          :key="p.user_id"
          class="wa-side-participant"
        >
          <ParticipantAvatar
            :name="p.display_name || p.name"
            :role="p.role"
            :image-url="participantAvatarUrl(p, teacherAvatarUrl, viewerId)"
            :size="48"
          />
          <div class="wa-side-participant__info min-w-0">
            <div class="text-subtitle-1 font-weight-bold text-truncate">
              {{ p.display_name || p.name }}
            </div>
            <v-chip size="x-small" :color="roleChipColor(p.role)" variant="flat" class="mt-1">
              {{ p.role_label || roleLabel(p.role) }}
            </v-chip>
          </div>
        </div>
        <v-divider class="my-4" />
        <div v-if="activeThread.course_context_label" class="metric-card mb-2">
          <div class="text-caption text-medium-emphasis">{{ t('messages.sidePanel.subjectCourse') }}</div>
          <div class="text-body-2 font-weight-medium text-primary">
            {{ activeThread.course_context_label }}
          </div>
        </div>
        <div class="metric-card mb-2">
          <div class="text-caption text-medium-emphasis">{{ t('messages.sidePanel.conversationType') }}</div>
          <div class="text-body-2 font-weight-medium">{{ threadTypeLabel }}</div>
        </div>
        <div v-if="activeThread.last_message_at" class="metric-card mb-2">
          <div class="text-caption text-medium-emphasis">{{ t('messages.sidePanel.lastMessage') }}</div>
          <div class="text-body-2">{{ formatListTime(activeThread.last_message_at) }}</div>
        </div>
        <v-btn
          v-if="profileTarget"
          class="mt-2"
          block
          variant="tonal"
          rounded="lg"
          prepend-icon="mdi-account"
          @click="$emit('open-profile', profileTarget)"
        >
          {{ t('messages.sidePanel.viewProfile') }}
        </v-btn>
      </template>
      <p v-else class="text-caption text-medium-emphasis text-center py-8">
        {{ t('messages.sidePanel.noDetails') }}
      </p>
    </div>

    <div v-if="activeThread && showParticipantBar" class="wa-side-panel__section px-4 pb-2">
      <div class="text-overline text-medium-emphasis mb-2">{{ t('messages.sidePanel.participants') }}</div>
      <ParticipantListBar
        :participants="activeThread.participants || []"
        :viewer-id="viewerId"
        :teacher-avatar-url="teacherAvatarUrl"
        class="wa-side-participant-bar"
      />
    </div>

    <div
      v-if="isTeacher && activeThread?.thread_type === 'teacher_student_parent'"
      class="wa-side-panel__section px-3 pb-4"
    >
      <div class="text-overline text-medium-emphasis mb-1 px-1">{{ t('messages.sidePanel.shareWithParents') }}</div>
      <GroupParticipantsManager
        :thread="activeThread"
        :contacts="messagingContacts"
        :is-teacher="isTeacher"
        @add-parent="$emit('add-parent', $event)"
        @remove-parent="$emit('remove-parent', $event)"
        @add-student="$emit('add-student')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import ParticipantListBar from './ParticipantListBar.vue'
import GroupParticipantsManager from './GroupParticipantsManager.vue'
import StudentContextPanel from './StudentContextPanel.vue'
import { formatListTime, roleChipColor, ROLE_LABELS, primaryOtherParticipant } from '../../utils/messagingUi.js'
import { participantAvatarUrl } from '../../utils/teacherAvatar.js'

const props = defineProps({
  viewerRole: { type: String, required: true },
  viewerId: { type: Number, default: null },
  activeThread: { type: Object, default: null },
  teacherCtx: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  teacherAvatarUrl: { type: String, default: null },
  isTeacher: { type: Boolean, default: false },
  messagingContacts: { type: Object, default: () => ({ parents: [], students: [] }) },
  showParticipantBar: { type: Boolean, default: false },
})

defineEmits(['open-profile', 'add-parent', 'remove-parent', 'add-student'])

const { t } = useI18n()

const otherParticipants = computed(() => {
  const t = props.activeThread
  if (!t?.participants?.length) return []
  return t.participants.filter((p) => p.user_id !== props.viewerId)
})

const threadTypeLabel = computed(() => {
  const map = {
    teacher_student: t('messages.threadTypes.teacherStudent'),
    teacher_parent: t('messages.threadTypes.teacherParent'),
    teacher_student_parent: t('messages.threadTypes.teacherStudentParent'),
  }
  return map[props.activeThread?.thread_type] || t('messages.conversation')
})

const profileTarget = computed(() => {
  const primary = primaryOtherParticipant(props.activeThread, props.viewerId)
  if (props.viewerRole === 'student' && primary?.role === 'teacher') return null
  if (primary?.role === 'student') return primary.user_id
  if (props.viewerRole === 'parent') {
    const student = otherParticipants.value.find((p) => p.role === 'student')
    return student?.user_id
  }
  return null
})

function roleLabel(role) {
  return ROLE_LABELS[role] || role
}
</script>

<style scoped>
.wa-side-panel {
  height: 100%;
  overflow-y: auto;
  direction: rtl;
}

.wa-side-participant {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.wa-side-panel__section {
  border-top: 1px solid var(--wa-border, var(--em-border-subtle));
  margin-top: 8px;
  padding-top: 12px;
}

.metric-card {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
