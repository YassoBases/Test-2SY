<template>
  <header class="wa-thread-header">
    <v-btn
      v-if="showBack"
      class="wa-back-btn"
      icon
      size="small"
      variant="text"
      :aria-label="t('messages.backToConversations')"
      @click="$emit('back')"
    >
      <v-icon>mdi-arrow-right</v-icon>
    </v-btn>

    <button
      type="button"
      class="wa-thread-header__avatar-btn"
      :title="infoButtonTitle"
      :aria-label="t('messages.conversationInfo')"
      @click="onInfoClick"
    >
      <ParticipantAvatar
        :name="headerName"
        :role="headerRole"
        :image-url="headerAvatarUrl"
        :size="44"
        :show-role-badge="false"
      />
    </button>

    <div class="wa-thread-header__info">
      <button
        v-if="headerClickable"
        type="button"
        class="wa-thread-header__name wa-thread-header__name--link"
        @click="onHeaderClick"
      >
        {{ headerName }}
      </button>
      <h2 v-else class="wa-thread-header__name">{{ headerName }}</h2>

      <div class="wa-thread-header__subtitle">
        <span v-if="subjectLabel" class="wa-thread-header__subject text-truncate">
          {{ subjectLabel }}
        </span>
        <template v-if="subjectLabel && presence">
          <span class="wa-thread-header__sep" aria-hidden="true">·</span>
        </template>
        <span v-if="presence" class="wa-thread-header__presence">
          <span
            class="wa-thread-header__presence-dot"
            :class="{ 'wa-thread-header__presence-dot--online': presence.online }"
          />
          {{ presence.text }}
        </span>
        <template v-else-if="!subjectLabel">
          <v-chip size="x-small" :color="roleChipColor(headerRole)" variant="flat" density="compact">
            {{ roleLabel(headerRole) }}
          </v-chip>
          <span v-if="secondaryMeta" class="text-truncate">{{ secondaryMeta }}</span>
        </template>
      </div>
    </div>

    <div class="wa-thread-header__actions">
      <v-btn
        icon
        size="small"
        variant="text"
        :title="t('messages.conversationInfo')"
        @click="onInfoClick"
      >
        <v-icon size="20">mdi-information-outline</v-icon>
      </v-btn>
      <v-btn icon size="small" variant="text" :title="t('messages.searchInMessages')" @click="toggleSearch">
        <v-icon size="20">{{ showSearch ? 'mdi-close' : 'mdi-magnify' }}</v-icon>
      </v-btn>
      <v-menu location="bottom end">
        <template #activator="{ props: menuProps }">
          <v-btn v-bind="menuProps" icon size="small" variant="text" :title="t('messages.more')">
            <v-icon size="20">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list density="compact" min-width="220">
          <v-list-item
            v-for="action in menuQuickActions"
            :key="action.id"
            :prepend-icon="action.icon"
            @click="action.onClick"
          >
            <v-list-item-title>{{ action.label }}</v-list-item-title>
          </v-list-item>
          <v-divider v-if="menuQuickActions.length" class="my-1" />
          <v-list-item prepend-icon="mdi-pin-outline" @click="$emit('toggle-pin')">
            <v-list-item-title>{{ thread.is_pinned ? t('messages.unpin') : t('messages.pin') }}</v-list-item-title>
          </v-list-item>
          <v-list-item prepend-icon="mdi-archive-outline" @click="$emit('toggle-archive')">
            <v-list-item-title>{{ thread.is_archived ? t('messages.unarchive') : t('messages.archive') }}</v-list-item-title>
          </v-list-item>
          <v-list-item prepend-icon="mdi-email-mark-as-unread" @click="$emit('mark-unread')">
            <v-list-item-title>{{ t('messages.markUnread') }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </header>

  <div v-if="showSearch" class="wa-thread-header__search">
    <v-text-field
      v-model="searchLocal"
      density="compact"
      variant="solo-filled"
      flat
      rounded="lg"
      hide-details
      prepend-inner-icon="mdi-magnify"
      :placeholder="t('messages.searchMessagesPlaceholder')"
      clearable
      @keyup.enter="$emit('search', searchLocal)"
      @click:clear="$emit('search', '')"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import {
  formatPresenceStatus,
  primaryOtherParticipant,
  roleChipColor,
  ROLE_LABELS,
} from '../../utils/messagingUi.js'
import { participantAvatarUrl, teacherImageFromEntity } from '../../utils/teacherAvatar.js'

const props = defineProps({
  thread: { type: Object, required: true },
  viewerRole: { type: String, default: 'teacher' },
  isTeacher: { type: Boolean, default: false },
  studentHeader: { type: Object, default: null },
  parentHeader: { type: Object, default: null },
  parentChatContext: { type: Object, default: null },
  courseContextLabel: { type: String, default: null },
  viewerId: { type: Number, default: null },
  teacherAvatarUrl: { type: String, default: null },
  showBack: { type: Boolean, default: false },
})

const emit = defineEmits([
  'back',
  'open-info',
  'open-profile',
  'open-student-profile',
  'open-teacher-profile',
  'parent-note',
  'quiz-results',
  'learning-progress',
  'toggle-pin',
  'toggle-archive',
  'mark-unread',
  'search',
])

const { t } = useI18n()

const showSearch = ref(false)
const searchLocal = ref('')

const primary = computed(() => primaryOtherParticipant(props.thread, props.viewerId))

const headerName = computed(() => {
  if (props.parentChatContext) return props.parentChatContext.teacher_name
  if (props.studentHeader) return props.studentHeader.full_name
  if (props.parentHeader) return props.parentHeader.parent_name
  const p = primary.value
  return p?.display_name || p?.name || props.thread.title
})

const headerRole = computed(() => {
  if (props.parentChatContext) return 'teacher'
  if (props.studentHeader) return 'student'
  if (props.parentHeader) return 'parent'
  return primary.value?.role || 'teacher'
})

const headerAvatarUrl = computed(() => {
  const parentImg = teacherImageFromEntity(props.parentChatContext)
  if (parentImg) return parentImg
  return participantAvatarUrl(primary.value, props.teacherAvatarUrl, props.viewerId)
})

const subjectLabel = computed(() => {
  if (props.parentChatContext?.subject_name) {
    const student = props.parentChatContext.student_name
    return student ? `${props.parentChatContext.subject_name} — ${student}` : props.parentChatContext.subject_name
  }
  if (props.courseContextLabel) return props.courseContextLabel
  if (props.studentHeader?.grade != null) return t('messages.grade', { grade: props.studentHeader.grade })
  return null
})

const presence = computed(() => formatPresenceStatus(primary.value))

const secondaryMeta = computed(() => {
  if (props.parentHeader?.linked_student_name) return props.parentHeader.linked_student_name
  return null
})

const headerClickable = computed(() => {
  if (props.isTeacher && props.studentHeader) return true
  if (props.parentHeader?.linked_student_id) return true
  return false
})

const infoButtonTitle = computed(() => t('messages.threadHeader.viewConversationInfo'))

const menuQuickActions = computed(() => {
  const actions = []
  if (props.isTeacher && props.studentHeader) {
    const sid = props.studentHeader.student_id
    actions.push(
      { id: 'profile', label: t('messages.threadHeader.studentProfile'), icon: 'mdi-account-school', onClick: () => emit('open-profile', sid) },
      { id: 'quiz', label: t('messages.threadHeader.quizResults'), icon: 'mdi-clipboard-check', onClick: () => emit('quiz-results', sid) },
      { id: 'progress', label: t('messages.threadHeader.learningProgress'), icon: 'mdi-chart-line', onClick: () => emit('learning-progress', sid) },
      { id: 'note', label: t('messages.threadHeader.parentNote'), icon: 'mdi-note-plus', onClick: () => emit('parent-note', sid) },
    )
  }
  return actions
})

function roleLabel(role) {
  return ROLE_LABELS[role] || role
}

function onHeaderClick() {
  if (props.studentHeader) emit('open-profile', props.studentHeader.student_id)
  else if (props.parentHeader) emit('open-student-profile', props.parentHeader.linked_student_id)
}

function onInfoClick() {
  emit('open-info')
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  if (!showSearch.value) {
    searchLocal.value = ''
    emit('search', '')
  }
}
</script>
