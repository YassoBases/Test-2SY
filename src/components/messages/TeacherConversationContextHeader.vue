<template>
  <header class="teacher-ctx-header teacher-ctx-header--compact">
    <v-progress-linear v-if="loading" indeterminate color="primary" class="teacher-ctx-header__loading" />

    <div v-else class="teacher-ctx-header__main">
      <v-btn
        v-if="showBack"
        class="teacher-ctx-header__back wa-back-btn"
        icon
        size="x-small"
        variant="text"
        :aria-label="t('messages.backToConversations')"
        @click="$emit('back')"
      >
        <v-icon size="18">mdi-arrow-right</v-icon>
      </v-btn>

      <ParticipantAvatar
        class="teacher-ctx-header__avatar"
        :name="displayName"
        :role="displayRole"
        :size="32"
        :show-role-badge="false"
      />

      <div class="teacher-ctx-header__content">
        <div class="teacher-ctx-header__row1">
          <div class="teacher-ctx-header__name-block min-w-0">
            <h2 class="teacher-ctx-header__name text-truncate">{{ displayName }}</h2>
            <TeacherLinkedParentsMenu
              v-if="showLinkedParents"
              :parents="linkedParents"
              :opening-parent-id="openingParentId"
              @message-parent="$emit('message-parent', $event)"
              @view-profile="$emit('open-student-drawer')"
            >
              <template #activator="{ props: menuProps }">
                <button type="button" class="teacher-ctx-header__linked-line" v-bind="menuProps">
                  👨‍👩‍👧 {{ t('messages.linkedParentsCount', { count: linkedParents.length }) }}
                </button>
              </template>
            </TeacherLinkedParentsMenu>
          </div>
          <v-chip
            v-if="parentMode"
            size="x-small"
            color="secondary"
            variant="tonal"
            class="teacher-ctx-header__role-chip"
          >
            {{ t('messages.roles.parent') }}
          </v-chip>
          <v-chip
            v-if="parentRelationshipText"
            size="x-small"
            color="secondary"
            variant="outlined"
            class="teacher-ctx-header__role-chip"
          >
            {{ parentRelationshipText }}
          </v-chip>
          <span v-if="presence" class="teacher-ctx-header__presence">
            <span
              class="teacher-ctx-header__presence-dot"
              :class="{ 'teacher-ctx-header__presence-dot--online': presence.online }"
            />
            {{ presence.text }}
          </span>
          <span v-else-if="student?.status && !parentMode" class="teacher-ctx-header__status">
            {{ student.status }}
          </span>
        </div>

        <p v-if="inlineMetaText" class="teacher-ctx-header__row2 text-truncate">
          {{ inlineMetaText }}
        </p>

        <div v-if="metricChips.length || showLinkedParents" class="teacher-ctx-header__row3">
          <TeacherLinkedParentsMenu
            v-if="showLinkedParents"
            :parents="linkedParents"
            :opening-parent-id="openingParentId"
            @message-parent="$emit('message-parent', $event)"
            @view-profile="$emit('open-student-drawer')"
          >
            <template #activator="{ props: menuProps }">
              <button type="button" class="teacher-ctx-header__parents-chip" v-bind="menuProps">
                👨‍👩‍👧 {{ t('messages.linkedParents.title') }} ({{ linkedParents.length }})
              </button>
            </template>
          </TeacherLinkedParentsMenu>
          <span
            v-for="chip in metricChips"
            :key="chip.id"
            class="teacher-ctx-header__chip"
            :title="chip.label"
          >
            <v-icon size="12" class="teacher-ctx-header__chip-icon">{{ chip.icon }}</v-icon>
            <span class="teacher-ctx-header__chip-value" :dir="chip.dir || 'auto'">{{ chip.value }}</span>
          </span>
        </div>

        <div v-else-if="!student && !parent && courseContextLabel" class="teacher-ctx-header__row2 text-truncate">
          {{ courseContextLabel }}
        </div>
      </div>

      <div class="teacher-ctx-header__aside">
        <div class="teacher-ctx-header__utils">
          <v-btn icon size="x-small" variant="text" :title="t('messages.searchInMessages')" @click="toggleSearch">
            <v-icon size="18">{{ showSearch ? 'mdi-close' : 'mdi-magnify' }}</v-icon>
          </v-btn>
          <v-btn icon size="x-small" variant="text" :title="t('messages.conversationInfo')" @click="$emit('open-info')">
            <v-icon size="18">mdi-information-outline</v-icon>
          </v-btn>
          <v-menu location="bottom end">
            <template #activator="{ props: menuProps }">
              <v-btn v-bind="menuProps" icon size="x-small" variant="text" :title="t('messages.more')">
                <v-icon size="18">mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list density="compact" min-width="220">
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

        <div v-if="showActions" class="teacher-ctx-header__actions">
          <v-tooltip v-if="linkedStudentId" :text="t('messages.studentProfile')" location="bottom">
            <template #activator="{ props: tipProps }">
              <v-btn
                v-bind="tipProps"
                icon
                size="x-small"
                variant="text"
                :aria-label="t('messages.studentProfile')"
                @click="$emit('open-student-drawer')"
              >
                <v-icon size="18">mdi-account-school</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip v-if="linkedStudentId" :text="t('messages.viewProgress')" location="bottom">
            <template #activator="{ props: tipProps }">
              <v-btn
                v-bind="tipProps"
                icon
                size="x-small"
                variant="text"
                :aria-label="t('messages.viewProgress')"
                @click="$emit('view-progress', linkedStudentId)"
              >
                <v-icon size="18">mdi-chart-line</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip v-if="courseId" :text="t('messages.openClass')" location="bottom">
            <template #activator="{ props: tipProps }">
              <v-btn
                v-bind="tipProps"
                icon
                size="x-small"
                variant="text"
                :aria-label="t('messages.openClass')"
                @click="$emit('open-class', courseId)"
              >
                <v-icon size="18">mdi-school-outline</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip :text="t('messages.sendNotification')" location="bottom">
            <template #activator="{ props: tipProps }">
              <v-btn
                v-bind="tipProps"
                icon
                size="x-small"
                variant="text"
                :aria-label="t('messages.sendNotification')"
                @click="$emit('send-notification')"
              >
                <v-icon size="18">mdi-bell-outline</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
        </div>
      </div>
    </div>

    <div v-if="showSearch" class="teacher-ctx-header__search">
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
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import TeacherLinkedParentsMenu from './TeacherLinkedParentsMenu.vue'
import { formatListTime, formatPresenceStatus, primaryOtherParticipant } from '../../utils/messagingUi.js'
import { relationshipLabelAr } from '../../utils/subscriptionStatus.js'

const props = defineProps({
  thread: { type: Object, required: true },
  student: { type: Object, default: null },
  parent: { type: Object, default: null },
  linkedParents: { type: Array, default: () => [] },
  openingParentId: { type: Number, default: null },
  parentRelationshipLabel: { type: String, default: '' },
  courseContextLabel: { type: String, default: '' },
  courseSubjectName: { type: String, default: '' },
  courseId: { type: Number, default: null },
  lessonsCompleted: { type: Number, default: null },
  completionPercent: { type: Number, default: null },
  averageQuizPercent: { type: Number, default: null },
  lastActivityAt: { type: String, default: null },
  loading: { type: Boolean, default: false },
  viewerId: { type: Number, default: null },
  showBack: { type: Boolean, default: false },
})

const emit = defineEmits([
  'back',
  'open-info',
  'open-student-drawer',
  'view-progress',
  'open-class',
  'send-notification',
  'message-parent',
  'toggle-pin',
  'toggle-archive',
  'mark-unread',
  'search',
])

const { t } = useI18n()

const showSearch = ref(false)
const searchLocal = ref('')

const parentMode = computed(() => Boolean(props.parent) && !props.student)

const showLinkedParents = computed(
  () => Boolean(props.student) && !parentMode.value && props.linkedParents.length > 0,
)

const parentRelationshipText = computed(() => {
  if (!parentMode.value || !props.parentRelationshipLabel) return ''
  return relationshipLabelAr(props.parentRelationshipLabel)
})

const primaryParticipant = computed(() => primaryOtherParticipant(props.thread, props.viewerId))

const presence = computed(() => formatPresenceStatus(primaryParticipant.value))

const displayName = computed(() => {
  if (parentMode.value) return props.parent.parent_name
  if (props.student) return props.student.full_name
  return props.thread.title || t('messages.conversation')
})

const displayRole = computed(() => {
  if (parentMode.value) return 'parent'
  if (props.student) return 'student'
  return 'teacher'
})

const subjectLabel = computed(() => {
  if (props.courseSubjectName) return props.courseSubjectName
  if (props.student?.enrolled_subjects?.length === 1) return props.student.enrolled_subjects[0]
  const label = props.courseContextLabel || ''
  if (label.includes(' — ')) return label.split(' — ')[0].trim()
  return label || null
})

const inlineMetaParts = computed(() => {
  const parts = []

  if (parentMode.value) {
    if (props.parent.student_grade != null) parts.push(t('messages.grade', { grade: props.parent.student_grade }))
    if (subjectLabel.value) parts.push(subjectLabel.value)
    if (props.parent.linked_student_name) parts.push(t('messages.studentLabel', { name: props.parent.linked_student_name }))
    if (props.parent.linked_student_id) parts.push(`#${props.parent.linked_student_id}`)
    return parts
  }

  if (props.student) {
    if (props.student.grade != null) parts.push(t('messages.grade', { grade: props.student.grade }))
    if (subjectLabel.value) parts.push(subjectLabel.value)
    if (props.student.student_id) parts.push(`#${props.student.student_id}`)
  }

  return parts
})

const inlineMetaText = computed(() => inlineMetaParts.value.join(' • '))

const resolvedMetrics = computed(() => ({
  completion: props.student?.completion_percent ?? props.completionPercent,
  quiz: props.student?.average_quiz_percent ?? props.averageQuizPercent,
  lastActive: props.student?.last_activity_at ?? props.lastActivityAt,
  lessonsCompleted: props.lessonsCompleted,
}))

const metricChips = computed(() => {
  const chips = []
  const m = resolvedMetrics.value

  if (m.completion != null && m.completion !== '') {
    chips.push({
      id: 'completion',
      icon: 'mdi-book-open-page-variant',
      label: t('messages.metrics.lessonCompletion'),
      value: `${m.completion}%`,
      dir: 'ltr',
    })
  }

  if (m.quiz != null && m.quiz !== '') {
    chips.push({
      id: 'quiz',
      icon: 'mdi-clipboard-text-outline',
      label: t('messages.metrics.quizAverage'),
      value: `${m.quiz}%`,
      dir: 'ltr',
    })
  }

  if (m.lastActive) {
    chips.push({
      id: 'last-active',
      icon: 'mdi-clock-outline',
      label: t('messages.metrics.lastActivity'),
      value: formatCompactDate(m.lastActive),
    })
  }

  if (m.lessonsCompleted != null && m.lessonsCompleted !== '') {
    chips.push({
      id: 'lessons',
      icon: 'mdi-check-circle-outline',
      label: t('messages.metrics.lessonsCompleted'),
      value: String(m.lessonsCompleted),
      dir: 'ltr',
    })
  }

  return chips
})

const linkedStudentId = computed(() => {
  if (props.student?.student_id) return props.student.student_id
  if (props.parent?.linked_student_id) return props.parent.linked_student_id
  return props.thread?.student_id || null
})

const showActions = computed(() => Boolean(linkedStudentId.value || props.courseId))

function formatCompactDate(iso) {
  if (!iso) return '—'
  const short = formatListTime(iso)
  if (short) return short
  try {
    return new Intl.DateTimeFormat('ar-SY', { dateStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  if (!showSearch.value) {
    searchLocal.value = ''
    emit('search', '')
  }
}
</script>
