<template>
  <div class="messages-page wa-messages-app slide-up-enter-active">
    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-2 rounded-lg">{{ error }}</v-alert>

    <div
      class="wa-shell"
      :class="{
        'wa-shell--mobile-thread': mobileInThread,
        'wa-shell--thread-open': !!selectedId && !!activeThread,
      }"
    >
      <aside
        class="wa-pane wa-pane--list"
        :class="{ 'wa-pane--hidden-mobile': mobileInThread }"
      >
        <div class="wa-list-header">
          <div class="wa-list-header__row">
            <h1 class="wa-list-header__title">{{ t('messages.title') }}</h1>
            <div class="d-flex align-center gap-1">
              <v-chip v-if="totalUnread > 0" color="error" size="x-small" variant="flat">
                {{ totalUnread }}
              </v-chip>
              <v-btn
                v-if="isTeacher"
                icon
                size="small"
                color="primary"
                variant="tonal"
                :title="t('messages.newConversation')"
                @click="showNewDialog = true"
              >
                <v-icon>mdi-message-plus</v-icon>
              </v-btn>
            </div>
          </div>
          <v-text-field
            v-model="search"
            class="wa-list-search"
            density="compact"
            variant="solo-filled"
            flat
            rounded="lg"
            hide-details
            prepend-inner-icon="mdi-magnify"
            :placeholder="t('messages.searchPlaceholder')"
          />
          <v-btn
            v-if="isTeacher"
            size="x-small"
            variant="text"
            class="mt-1 px-0"
            :prepend-icon="showArchived ? 'mdi-archive-arrow-up' : 'mdi-archive-outline'"
            @click="toggleShowArchived"
          >
            {{ showArchived ? t('messages.hideArchived') : t('messages.archived') }}
          </v-btn>
        </div>
        <v-progress-linear v-if="loadingList" indeterminate color="primary" />
        <div v-else class="wa-list-body chat-scroll">
          <template v-if="isParent">
            <div class="wa-list-section-title">{{ t('messages.parentTeachersSection') }}</div>
            <ParentTeacherContactItem
              v-for="contact in filteredParentTeachers"
              :key="`${contact.teacher_user_id}-${contact.student_id}-${contact.course_id}`"
              :contact="contact"
              :active="selectedId === contact.thread_id"
              @select="openParentTeacherChat"
            />
            <MessagesEmptyState
              v-if="!filteredParentTeachers.length"
              variant="compact"
              icon="mdi-account-school-outline"
              :icon-size="40"
              :title="t('messages.noTeachers')"
              :subtitle="t('messages.noTeachersHint')"
            />
          </template>
          <template v-else>
          <ConversationListItem
            v-for="conv in filteredConversations"
            :key="conv.id"
            :conv="conv"
            :viewer-id="user?.id"
            :active="selectedId === conv.id"
            :teacher-avatar-url="teacherAvatarUrl"
            :parent-relationships="parentRelationshipCache"
            @select="selectConversation"
          />
          <MessagesEmptyState
            v-if="!filteredConversations.length"
            variant="compact"
            icon="mdi-forum-outline"
            :icon-size="40"
            :title="isTeacher ? t('messages.noConversations') : t('messages.noConversationsYet')"
            :subtitle="isTeacher ? t('messages.startNewConversation') : t('messages.conversationsAppearHere')"
          >
            <v-btn
              v-if="isTeacher"
              size="small"
              color="primary"
              variant="tonal"
              rounded="lg"
              prepend-icon="mdi-plus"
              @click="showNewDialog = true"
            >
              {{ t('messages.newConversation') }}
            </v-btn>
          </MessagesEmptyState>
          </template>
        </div>
      </aside>

      <main
        class="wa-pane wa-pane--chat"
        :class="{ 'wa-pane--hidden-mobile': mobileInThread === false && !mdAndUp && !selectedId }"
      >
        <div v-if="selectedId && activeThread" class="wa-chat-panel">
          <TeacherConversationContextHeader
            v-if="isTeacher"
            :thread="activeThread"
            :student="threadContext?.student"
            :parent="threadContext?.parent"
            :linked-parents="activeLinkedParents"
            :opening-parent-id="openingParentId"
            :parent-relationship-label="activeParentRelationshipLabel"
            :course-context-label="activeCourseContextLabel"
            :course-subject-name="activeThread.course_subject_name"
            :course-id="activeThread.course_id"
            :lessons-completed="headerMetrics.lessonsCompleted"
            :completion-percent="headerMetrics.completion"
            :average-quiz-percent="headerMetrics.quiz"
            :last-activity-at="headerMetrics.lastActive"
            :loading="loadingContext"
            :viewer-id="user?.id"
            :show-back="mobileInThread"
            @back="goBackToList"
            @open-info="openInfoDrawer"
            @open-student-drawer="openStudentDrawer"
            @view-progress="openStudentDrawer"
            @open-class="openClass"
            @send-notification="openNotificationRecipientsDialog"
            @message-parent="openParentConversation"
            @toggle-pin="togglePin"
            @toggle-archive="toggleArchive"
            @mark-unread="markUnread"
            @search="onSearchMessages"
          />
          <ConversationThreadHeader
            v-else
            :thread="activeThread"
            :viewer-role="props.role"
            :is-teacher="isTeacher"
            :student-header="threadContext?.student"
            :parent-header="threadContext?.parent"
            :parent-chat-context="parentChatContext"
            :course-context-label="activeCourseContextLabel"
            :viewer-id="user?.id"
            :teacher-avatar-url="teacherAvatarUrl"
            :show-back="mobileInThread"
            @back="goBackToList"
            @open-info="openInfoDrawer"
            @open-profile="openStudentProfile"
            @open-student-profile="openStudentProfile"
            @open-teacher-profile="openTeacherSelfProfile"
            @parent-note="openParentNote"
            @quiz-results="openQuizResults"
            @learning-progress="openLearningProgress"
            @toggle-pin="togglePin"
            @toggle-archive="toggleArchive"
            @mark-unread="markUnread"
            @search="onSearchMessages"
          />

          <v-alert
            v-if="searchHits.length"
            type="info"
            variant="tonal"
            density="compact"
            class="mx-3 my-1 rounded-lg"
          >
            {{ t('messages.searchResults', { count: searchHits.length }) }}
          </v-alert>

          <v-progress-linear v-if="loadingThread" indeterminate color="primary" />

          <div ref="threadScroll" class="wa-timeline chat-scroll">
            <div class="wa-timeline-inner">
              <MessagesEmptyState
                v-if="!displayMessages.length && !loadingThread"
                variant="compact"
                icon="mdi-message-outline"
                :icon-size="36"
                :title="t('messages.noMessages')"
                :subtitle="t('messages.sendFirstMessage')"
              />
              <MessageBubble
                v-for="(msg, idx) in displayMessages"
                :key="msg.id"
                :msg="msg"
                :viewer-id="currentViewerId"
                :participants="activeThread.participants"
                :is-group="isGroupThread"
                :teacher-avatar-url="teacherAvatarUrl"
                :animation-delay="Math.min(idx * 25, 200)"
                @delete="onDeleteMessage"
              />
            </div>
          </div>

          <div class="wa-compose-bar">
            <MessageComposer
              ref="composer"
              :sending="sending"
              @send-text="sendTextMessage"
              @send-attachment="sendAttachmentMessage"
              @error="onComposerError"
            />
          </div>

          <!-- Info drawer: overlay inside chat only, never a shell column -->
          <Transition name="wa-info-slide">
            <div v-if="contextDrawer" class="wa-info-layer" role="dialog" aria-modal="true" :aria-label="t('messages.conversationInfo')">
              <button type="button" class="wa-info-backdrop" :aria-label="t('common.close')" @click="closeInfoDrawer" />
              <aside class="wa-info-panel">
                <div class="wa-info-panel__head">
                  <h3 class="wa-info-panel__title">{{ t('messages.conversationInfo') }}</h3>
                  <v-btn icon size="small" variant="text" :aria-label="t('common.close')" @click="closeInfoDrawer">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                </div>
                <ConversationSidePanel
                  :viewer-role="props.role"
                  :viewer-id="user?.id"
                  :active-thread="activeThread"
                  :teacher-ctx="threadContext"
                  :loading="loadingContext"
                  :teacher-avatar-url="teacherAvatarUrl"
                  :is-teacher="isTeacher"
                  :messaging-contacts="messagingContacts"
                  :show-participant-bar="showParticipantBar"
                  @open-profile="openStudentDrawer"
                  @add-parent="onAddParent"
                  @remove-parent="onRemoveParent"
                  @add-student="onAddStudent"
                />
              </aside>
            </div>
          </Transition>

          <TeacherStudentProfileDrawer
            v-if="isTeacher"
            v-model="studentProfileDrawer"
            :student-id="activeStudentId"
            :course-id="activeThread.course_id"
            :cached-profile="activeStudentProfile"
            @send-notification="openNotificationRecipientsDialog"
            @view-quizzes="openQuizResults"
            @open-class="openClass"
            @open-full-profile="navigateToFullStudentProfile"
          />
        </div>

        <div v-else class="wa-chat-empty">
          <MessagesEmptyState
            icon="mdi-message-text-outline"
            :icon-size="56"
            :title="t('messages.selectConversation')"
            :subtitle="isTeacher ? t('messages.selectFromList') : t('messages.selectToStart')"
          />
        </div>
      </main>
    </div>

    <NewConversationDialog v-if="isTeacher" v-model="showNewDialog" @created="onConversationCreated" />

    <TeacherNotificationRecipientsDialog
      v-if="isTeacher"
      v-model="showNotificationDialog"
      :student-name="notificationStudentName"
      :show-student="Boolean(notificationStudentId)"
      :parents="notificationLinkedParents"
      @confirm="onNotificationRecipientsConfirm"
    />

    <v-snackbar v-model="snackbarOpen" :timeout="5000" location="bottom" color="surface-variant">
      {{ snackbarMessage }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import ConversationListItem from '../../components/messages/ConversationListItem.vue'
import ConversationThreadHeader from '../../components/messages/ConversationThreadHeader.vue'
import TeacherConversationContextHeader from '../../components/messages/TeacherConversationContextHeader.vue'
import TeacherStudentProfileDrawer from '../../components/messages/TeacherStudentProfileDrawer.vue'
import MessagesEmptyState from '../../components/messages/MessagesEmptyState.vue'
import MessageBubble from '../../components/messages/MessageBubble.vue'
import MessageComposer from '../../components/messages/MessageComposer.vue'
import NewConversationDialog from '../../components/messages/NewConversationDialog.vue'
import TeacherNotificationRecipientsDialog from '../../components/messages/TeacherNotificationRecipientsDialog.vue'
import ConversationSidePanel from '../../components/messages/ConversationSidePanel.vue'
import ParentTeacherContactItem from '../../components/parent/ParentTeacherContactItem.vue'
import { fetchParentTeachers, openParentTeacherChat as apiOpenParentTeacherChat } from '../../api/parentMessaging.js'
import {
  ensureTeacherProfile,
  invalidateTeacherProfileCache,
  useTeacherProfile,
} from '../../composables/useTeacherProfile.js'
import '../../assets/styles/messages-chat.css'
import '../../assets/styles/ui-6.4-course-messages.css'
import '../../assets/styles/ui-msg-7-messages.css'
import {
  buildLinkedParentsMenuItems,
  cacheParentRelationships,
  findTeacherParentThread,
  parentRelationshipFromCache,
} from '../../utils/messagingUi.js'
import {
  createConversation,
  deleteConversationMessage,
  fetchConversation,
  fetchConversationContext,
  fetchConversations,
  fetchConversationsUnreadCount,
  fetchMessagingContacts,
  markConversationUnread,
  searchConversationMessages,
  sendConversationAttachment,
  sendConversationMessage,
  updateConversationParticipants,
  updateConversationSettings,
} from '../../api/messages.js'
import { getErrorMessage } from '../../api/client.js'
import { fetchTeacherStudentProfile } from '../../api/teacherStudents.js'
import { useAuth } from '../../composables/useAuth.js'

const props = defineProps({
  role: { type: String, required: true },
})

const { t } = useI18n()

const { user } = useAuth()
const route = useRoute()
const router = useRouter()
const { mdAndUp } = useDisplay()

/** Logged-in user id — must match message.sender_id for is_mine alignment. */
const currentViewerId = computed(() => {
  const u = user.value
  if (!u) return null
  const raw = u.id ?? u.user_id ?? u.userId
  if (raw == null || raw === '') return null
  const n = Number(raw)
  return Number.isFinite(n) ? n : null
})

const isTeacher = computed(() => props.role === 'teacher')
const isParent = computed(() => props.role === 'parent')
const mobileInThread = computed(() => !mdAndUp.value && !!selectedId.value)

const parentTeachers = ref([])
const parentChatContext = ref(null)
const openingParentChat = ref(false)

const loadingList = ref(true)
const loadingThread = ref(false)
const sending = ref(false)
const error = ref('')
const search = ref('')
const conversations = ref([])
const totalUnread = ref(0)
const selectedId = ref(null)
const activeThread = ref(null)
const threadContext = ref(null)
const loadingContext = ref(false)
const messagingContacts = ref({ parents: [], students: [] })
const searchHits = ref([])
const showNewDialog = ref(false)
const showArchived = ref(false)
const contextDrawer = ref(false)
const studentProfileDrawer = ref(false)
const activeStudentProfile = ref(null)
const parentRelationshipCache = ref({})
const relationshipPrefetchStarted = new Set()
const showNotificationDialog = ref(false)
const openingParentId = ref(null)
const snackbarOpen = ref(false)
const snackbarMessage = ref('')
const threadScroll = ref(null)
const composer = ref(null)

function openInfoDrawer() {
  contextDrawer.value = true
}

function closeInfoDrawer() {
  contextDrawer.value = false
}

const activeStudentId = computed(() => {
  if (threadContext.value?.student?.student_id) return threadContext.value.student.student_id
  if (threadContext.value?.parent?.linked_student_id) return threadContext.value.parent.linked_student_id
  return activeThread.value?.student_id || null
})

async function loadStudentProfileSummary(studentId) {
  if (!isTeacher.value || !studentId) {
    activeStudentProfile.value = null
    return
  }
  try {
    activeStudentProfile.value = await fetchTeacherStudentProfile(studentId)
    parentRelationshipCache.value = cacheParentRelationships(
      parentRelationshipCache.value,
      studentId,
      activeStudentProfile.value?.linked_parents || [],
    )
  } catch {
    activeStudentProfile.value = null
  }
}

const activeLinkedParents = computed(() => {
  const studentId = activeStudentId.value
  const linked = activeStudentProfile.value?.linked_parents || []
  if (!studentId || !linked.length) return []
  return buildLinkedParentsMenuItems(linked, studentId, conversations.value)
})

const activeParentRelationshipLabel = computed(() => {
  const parent = threadContext.value?.parent
  if (!parent?.parent_id || !parent.linked_student_id) return ''
  return parentRelationshipFromCache(
    parentRelationshipCache.value,
    parent.parent_id,
    parent.linked_student_id,
  ) || ''
})

const notificationStudentId = computed(() => activeStudentId.value)

const notificationStudentName = computed(() => {
  return (
    threadContext.value?.student?.full_name
    || activeStudentProfile.value?.info?.full_name
    || activeThread.value?.student_name
    || ''
  )
})

const notificationLinkedParents = computed(() => activeStudentProfile.value?.linked_parents || [])

const isStudentThread = computed(() => activeThread.value?.thread_type === 'teacher_student')

const activeCourseContextLabel = computed(
  () =>
    activeThread.value?.course_context_label ||
    threadContext.value?.course_context_label ||
    null,
)

const headerMetrics = computed(() => {
  const s = threadContext.value?.student
  const p = activeStudentProfile.value
  return {
    completion: s?.completion_percent ?? p?.analytics?.completion_percent ?? null,
    quiz: s?.average_quiz_percent ?? p?.analytics?.average_score_percent ?? null,
    lastActive: s?.last_activity_at ?? p?.analytics?.last_active_date ?? null,
    lessonsCompleted: p?.learning?.lessons_completed ?? null,
  }
})

const showParticipantBar = computed(() => {
  const t = activeThread.value?.thread_type
  return t === 'teacher_student_parent' || (activeThread.value?.participants?.length || 0) > 2
})

const isGroupThread = computed(() => {
  const t = activeThread.value?.thread_type
  return t === 'teacher_student_parent' || (activeThread.value?.participants?.length || 0) > 2
})

const { teacherProfile } = useTeacherProfile()
const teacherAvatarUrl = computed(() => teacherProfile.value?.image_url || null)

let pollTimer = null

const displayMessages = computed(() => {
  if (searchHits.value.length) return searchHits.value
  return activeThread.value?.messages || []
})

const filteredParentTeachers = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return parentTeachers.value
  return parentTeachers.value.filter(
    (c) =>
      c.teacher_name?.toLowerCase().includes(q) ||
      c.subject_name?.toLowerCase().includes(q) ||
      c.student_name?.toLowerCase().includes(q) ||
      c.last_message_preview?.toLowerCase().includes(q),
  )
})

const filteredConversations = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return conversations.value
  return conversations.value.filter(
    (c) =>
      c.title?.toLowerCase().includes(q) ||
      c.course_context_label?.toLowerCase().includes(q) ||
      c.last_message_preview?.toLowerCase().includes(q) ||
      c.participants?.some(
        (p) =>
          p.name?.toLowerCase().includes(q) ||
          p.display_name?.toLowerCase().includes(q) ||
          p.role_label?.toLowerCase().includes(q),
      ),
  )
})

function goBackToList() {
  selectedId.value = null
  activeThread.value = null
  parentChatContext.value = null
  activeStudentProfile.value = null
  searchHits.value = []
  closeInfoDrawer()
  studentProfileDrawer.value = false
  const base =
    props.role === 'teacher' ? '/teacher/messages' : props.role === 'parent' ? '/parent/messages' : '/student/messages'
  router.replace({ path: base })
}

async function loadContext(threadId) {
  if (!isTeacher.value) return
  loadingContext.value = true
  try {
    threadContext.value = await fetchConversationContext(threadId)
    const studentId =
      threadContext.value?.student?.student_id
      || threadContext.value?.parent?.linked_student_id
      || activeThread.value?.student_id
    await loadStudentProfileSummary(studentId)
  } catch {
    threadContext.value = null
    activeStudentProfile.value = null
  } finally {
    loadingContext.value = false
  }
}

async function loadParentTeachers() {
  const data = await fetchParentTeachers()
  parentTeachers.value = data.teachers || []
  if (isParent.value) {
    totalUnread.value = data.total_unread ?? 0
  }
}

function parseThreadId(raw) {
  const n = Number(raw)
  return Number.isFinite(n) && n > 0 ? n : null
}

async function loadList() {
  try {
    if (isParent.value) {
      await loadParentTeachers()
    }
    const data = await fetchConversations(showArchived.value)
    conversations.value = data.conversations || []
    if (!isParent.value) {
      totalUnread.value = data.total_unread ?? 0
    }
    if (isTeacher.value) {
      await prefetchParentRelationshipsForList()
    }
    error.value = ''
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.loadConversations'))
  } finally {
    loadingList.value = false
  }
}

async function prefetchParentRelationshipsForList() {
  const studentIds = new Set()
  for (const conv of conversations.value) {
    if (conv.thread_type === 'teacher_parent' && conv.student_id) {
      if (!relationshipPrefetchStarted.has(conv.student_id)) {
        studentIds.add(conv.student_id)
      }
    }
  }
  for (const studentId of studentIds) {
    relationshipPrefetchStarted.add(studentId)
    try {
      const profile = await fetchTeacherStudentProfile(studentId)
      parentRelationshipCache.value = cacheParentRelationships(
        parentRelationshipCache.value,
        studentId,
        profile.linked_parents || [],
      )
    } catch {
      /* optional */
    }
  }
}

async function openParentTeacherChat(contact) {
  if (openingParentChat.value) return
  openingParentChat.value = true
  error.value = ''
  try {
    const result = await apiOpenParentTeacherChat(contact.teacher_user_id, {
      studentId: contact.student_id,
      courseId: contact.course_id,
    })
    parentChatContext.value = {
      teacher_name: result.teacher_name,
      subject_name: result.subject_name,
      student_name: result.student_name,
      teacher_image_url: contact.teacher_image_url,
      context_label: result.context_label,
    }
    const idx = parentTeachers.value.findIndex(
      (c) =>
        c.teacher_user_id === contact.teacher_user_id &&
        c.student_id === contact.student_id &&
        c.course_id === contact.course_id,
    )
    if (idx >= 0) {
      parentTeachers.value[idx] = {
        ...parentTeachers.value[idx],
        thread_id: result.thread_id,
        unread_count: 0,
      }
    }
    await selectConversation(result.thread_id)
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.openConversation'))
  } finally {
    openingParentChat.value = false
  }
}

async function loadUnread() {
  try {
    const data = await fetchConversationsUnreadCount()
    totalUnread.value = data.unread_count ?? 0
  } catch {
    /* ignore */
  }
}

function applyThreadReadLocally(threadId) {
  const idx = conversations.value.findIndex((c) => c.id === threadId)
  if (idx >= 0) {
    const prev = conversations.value[idx].unread_count || 0
    conversations.value[idx] = { ...conversations.value[idx], unread_count: 0 }
    if (!isParent.value && prev > 0) {
      totalUnread.value = Math.max(0, totalUnread.value - prev)
    }
  }
  parentTeachers.value = parentTeachers.value.map((c) =>
    c.thread_id === threadId ? { ...c, unread_count: 0 } : c,
  )
  if (isParent.value) {
    totalUnread.value = parentTeachers.value.reduce((sum, c) => sum + (c.unread_count || 0), 0)
  }
}

async function loadThread(id, markRead = true) {
  loadingThread.value = true
  searchHits.value = []
  if (markRead) applyThreadReadLocally(id)
  try {
    const detail = await fetchConversation(id, markRead)
    activeThread.value = { ...detail, unread_count: markRead ? 0 : detail.unread_count }
    if (markRead) applyThreadReadLocally(id)
    await loadList()
    if (isParent.value) {
      const match = parentTeachers.value.find((c) => c.thread_id === id)
      if (match) {
        parentChatContext.value = {
          teacher_name: match.teacher_name,
          subject_name: match.subject_name,
          student_name: match.student_name,
          teacher_image_url: match.teacher_image_url,
          context_label: `${match.subject_name} — ${match.student_name}`,
        }
      }
    }
    await loadContext(id)
    await scrollToBottom()
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.loadThread'))
  } finally {
    loadingThread.value = false
  }
}

async function selectConversation(id) {
  closeInfoDrawer()
  studentProfileDrawer.value = false
  selectedId.value = id
  const base =
    props.role === 'teacher' ? '/teacher/messages' : props.role === 'parent' ? '/parent/messages' : '/student/messages'
  router.replace({ path: base, query: { thread: id } })
  await loadThread(id)
}

async function sendTextMessage(text) {
  if (!text?.trim() || !selectedId.value) return
  sending.value = true
  try {
    activeThread.value = await sendConversationMessage(selectedId.value, text.trim())
    composer.value?.clearDraft()
    await loadList()
    await scrollToBottom()
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.sendMessage'))
  } finally {
    sending.value = false
  }
}

async function sendAttachmentMessage({ file, caption, voiceDurationMs }) {
  if (!selectedId.value || !file) return
  sending.value = true
  error.value = ''
  try {
    activeThread.value = await sendConversationAttachment(selectedId.value, file, {
      caption,
      voiceDurationMs,
    })
    composer.value?.clearDraft()
    await loadList()
    await scrollToBottom()
  } catch (e) {
    const msg = getErrorMessage(e, t('messages.errors.sendAttachment'))
    error.value = msg
    onComposerError(msg)
  } finally {
    sending.value = false
  }
}

function onComposerError(msg) {
  if (msg) error.value = msg
}

async function onDeleteMessage(messageId) {
  try {
    await deleteConversationMessage(messageId)
    activeThread.value = await fetchConversation(selectedId.value, false)
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.deleteMessage'))
  }
}

async function onSearchMessages(q) {
  if (!selectedId.value || !q?.trim()) {
    searchHits.value = []
    return
  }
  try {
    const data = await searchConversationMessages(selectedId.value, q.trim())
    searchHits.value = data.messages || []
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.search'))
  }
}

async function togglePin() {
  if (!activeThread.value) return
  await updateConversationSettings(activeThread.value.id, { is_pinned: !activeThread.value.is_pinned })
  await loadList()
  activeThread.value = await fetchConversation(activeThread.value.id, false)
}

async function toggleArchive() {
  if (!activeThread.value) return
  await updateConversationSettings(activeThread.value.id, { is_archived: !activeThread.value.is_archived })
  await loadList()
  if (activeThread.value.is_archived) {
    selectedId.value = null
    activeThread.value = null
    goBackToList()
  } else {
    activeThread.value = await fetchConversation(activeThread.value.id, false)
  }
}

async function markUnread() {
  if (!activeThread.value) return
  await markConversationUnread(activeThread.value.id)
  await loadList()
}

function openStudentProfile(studentId) {
  if (isTeacher.value) {
    openStudentDrawer(studentId)
    return
  }
  if (props.role === 'parent') {
    router.push({ name: 'parent-dashboard' })
  } else {
    router.push({ name: 'student-profile' })
  }
}

function openStudentDrawer(studentId) {
  const id = Number(studentId || activeStudentId.value)
  if (!id) return
  if (studentId && studentId !== activeStudentId.value) {
    loadStudentProfileSummary(id)
  }
  studentProfileDrawer.value = true
}

function navigateToFullStudentProfile(studentId) {
  studentProfileDrawer.value = false
  router.push({ name: 'teacher-student-profile', params: { studentId: String(studentId) } })
}

function openClass(courseId) {
  if (!courseId) return
  router.push({ name: 'teacher-grade-detail', params: { courseId: String(courseId) } })
}

function focusComposerForNotification() {
  studentProfileDrawer.value = false
  closeInfoDrawer()
  nextTick(() => {
    composer.value?.focusInput?.()
  })
}

function openNotificationRecipientsDialog() {
  if (!notificationStudentId.value && !notificationLinkedParents.value.length) {
    focusComposerForNotification()
    return
  }
  studentProfileDrawer.value = false
  closeInfoDrawer()
  showNotificationDialog.value = true
}

function showSnackbar(message) {
  snackbarMessage.value = message
  snackbarOpen.value = true
}

async function onNotificationRecipientsConfirm({ includeStudent, parentIds }) {
  const studentId = notificationStudentId.value
  const parentOnly = parentIds.length > 0 && !includeStudent
  const studentAndParents = includeStudent && parentIds.length > 0

  if (includeStudent && isStudentThread.value) {
    focusComposerForNotification()
    if (studentAndParents) {
      showSnackbar(t('messages.snackbar.completeStudentFirst'))
    }
    return
  }

  if (includeStudent && studentId && !isStudentThread.value) {
    const studentThread = conversations.value.find(
      (c) => c.student_id === studentId && c.thread_type === 'teacher_student',
    )
    if (studentThread) {
      await selectConversation(studentThread.id)
      focusComposerForNotification()
      if (studentAndParents) {
        showSnackbar(t('messages.snackbar.completeStudentFirst'))
      }
      return
    }
  }

  if (parentOnly || parentIds.length) {
    const firstParentId = parentIds[0]
    if (firstParentId) {
      await openParentConversation(firstParentId)
      focusComposerForNotification()
      if (parentIds.length > 1) {
        showSnackbar(t('messages.snackbar.moreParents', { count: parentIds.length - 1 }))
      }
    }
  }
}

async function openParentConversation(parentId) {
  const studentId = activeStudentId.value
  if (!studentId || openingParentId.value) return
  openingParentId.value = parentId
  error.value = ''
  try {
    let thread = findTeacherParentThread(conversations.value, studentId, parentId)
    if (!thread?.id) {
      const created = await createConversation({
        student_id: studentId,
        parent_ids: [parentId],
        include_student: false,
      })
      await loadList()
      thread = created
    }
    if (thread?.id) {
      await selectConversation(thread.id)
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.openParentConversation'))
  } finally {
    openingParentId.value = null
  }
}

function openTeacherSelfProfile() {
  if (isTeacher.value) router.push({ name: 'teacher-profile' })
}

function openParentNote(studentId) {
  router.push({
    name: 'teacher-student-profile',
    params: { studentId: String(studentId) },
    query: { tab: 'parent-notes' },
  })
}

async function toggleShowArchived() {
  showArchived.value = !showArchived.value
  await loadList()
}

function openQuizResults(studentId) {
  router.push({ name: 'teacher-quizzes', query: { student: studentId } })
}

function openLearningProgress(studentId) {
  router.push({ name: 'teacher-student-profile', params: { studentId: String(studentId) } })
}

async function onAddParent(parentId) {
  activeThread.value = await updateConversationParticipants(activeThread.value.id, {
    add_parent_ids: [parentId],
  })
  await loadList()
}

async function onRemoveParent(parentId) {
  activeThread.value = await updateConversationParticipants(activeThread.value.id, {
    remove_parent_ids: [parentId],
  })
  await loadList()
}

async function onAddStudent() {
  activeThread.value = await updateConversationParticipants(activeThread.value.id, {
    include_student: true,
  })
  await loadList()
}

async function scrollToBottom() {
  await nextTick()
  const el = threadScroll.value
  if (el) el.scrollTop = el.scrollHeight
}

function onConversationCreated(thread) {
  showNewDialog.value = false
  conversations.value = [thread, ...conversations.value.filter((c) => c.id !== thread.id)]
  selectConversation(thread.id)
}

function startPolling() {
  pollTimer = setInterval(async () => {
    if (document.hidden) return
    await loadList()
    if (selectedId.value) {
      try {
        activeThread.value = await fetchConversation(selectedId.value, true)
        await scrollToBottom()
      } catch {
        /* ignore */
      }
    } else {
      await loadUnread()
    }
  }, 12000)
}

onMounted(async () => {
  if (isTeacher.value) {
    await ensureTeacherProfile()
    try {
      messagingContacts.value = await fetchMessagingContacts()
    } catch {
      /* optional */
    }
  }
  if (isTeacher.value) {
    await ensureTeacherProfile().catch(() => {})
  } else {
    invalidateTeacherProfileCache()
  }
  await loadList()
  const tid = parseThreadId(route.query.thread)
  if (tid) {
    selectedId.value = tid
    await loadThread(tid)
  }
  startPolling()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

watch(
  () => route.query.thread,
  async (tid) => {
    const parsed = parseThreadId(tid)
    if (parsed && parsed !== selectedId.value) {
      selectedId.value = parsed
      await loadThread(parsed)
    }
  },
)
</script>

<style scoped>
.messages-page {
  padding: 0;
}

.wa-list-section-title {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--em-primary-deep);
  padding: 10px 14px 6px;
}
</style>
