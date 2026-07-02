<template>
  <div class="parent-note-thread mb-3">
    <ParentNoteCard
      :note="displayNote"
      :unread="role === 'parent' && !displayNote.is_read_by_viewer"
      :formatted-date="formatDate(displayNote.created_at)"
      :clamp-body="!expanded"
    >
      <template #chips>
        <v-chip size="x-small" :color="statusColor" variant="tonal">
          {{ noteStatus(displayNote.status, displayNote.status_label_ar) }}
        </v-chip>
        <v-chip
          size="x-small"
          :color="priorityColor"
          variant="tonal"
          :prepend-icon="priorityIcon"
        >
          {{ notePriority(displayNote.priority, displayNote.priority_label_ar) }}
        </v-chip>
        <v-chip v-if="displayNote.reply_count > 0" size="x-small" variant="outlined" color="secondary">
          {{ t('parent.notes.repliesCount', { n: displayNote.reply_count }) }}
        </v-chip>
        <slot name="chips" />
      </template>
      <template #actions>
        <div class="d-flex flex-column align-end gap-1 flex-shrink-0">
          <v-btn
            size="small"
            variant="text"
            color="secondary"
            :prepend-icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
            @click="toggleExpand"
          >
            {{ expanded ? t('parent.notes.hideConversation') : t('parent.notes.showConversation') }}
          </v-btn>
          <slot name="actions" />
        </div>
      </template>
    </ParentNoteCard>

    <v-expand-transition>
      <div v-if="expanded" class="thread-panel pa-4 rounded-lg mt-2">
        <v-progress-linear v-if="loadingThread" indeterminate color="primary" class="mb-3" />

        <div v-else class="thread-messages">
          <div class="thread-message thread-message--root">
            <div class="thread-message__badge">
              <v-icon size="16">mdi-school</v-icon>
            </div>
            <div class="thread-message__bubble">
              <div class="thread-message__author">{{ displayNote.created_by_name }} · {{ t('parent.notes.teacherRole') }}</div>
              <p class="thread-message__body mb-0">{{ displayNote.description }}</p>
              <div class="thread-message__time">{{ formatDate(displayNote.created_at) }}</div>
            </div>
          </div>

          <div
            v-for="reply in threadReplies"
            :key="reply.id"
            class="thread-message"
            :class="reply.author_role === 'parent' ? 'thread-message--parent' : 'thread-message--teacher'"
          >
            <div class="thread-message__badge">
              <v-icon size="16">
                {{ reply.author_role === 'parent' ? 'mdi-account-heart' : 'mdi-school' }}
              </v-icon>
            </div>
            <div class="thread-message__bubble">
              <div class="d-flex align-center justify-space-between gap-2 mb-1">
                <div class="thread-message__author">
                  {{ reply.author_name }} · {{ reply.author_role === 'parent' ? t('parent.notes.parentRole') : t('parent.notes.teacherRole') }}
                </div>
                <div v-if="reply.can_edit" class="d-flex gap-0">
                  <v-btn icon size="x-small" variant="text" @click="startEditReply(reply)">
                    <v-icon size="16">mdi-pencil-outline</v-icon>
                  </v-btn>
                  <v-btn icon size="x-small" variant="text" color="error" @click="removeReply(reply)">
                    <v-icon size="16">mdi-delete-outline</v-icon>
                  </v-btn>
                </div>
              </div>
              <p v-if="editingReplyId !== reply.id" class="thread-message__body mb-0">{{ reply.body }}</p>
              <div v-else class="mt-2">
                <v-textarea v-model="editReplyBody" variant="outlined" rows="2" density="compact" hide-details />
                <div class="d-flex gap-2 mt-2">
                  <v-btn size="x-small" class="btn-glow" :loading="saving" @click="saveEditReply(reply)">{{ t('parent.common.save') }}</v-btn>
                  <v-btn size="x-small" variant="text" @click="cancelEditReply">{{ t('parent.common.cancel') }}</v-btn>
                </div>
              </div>
              <div class="thread-message__time">{{ formatDate(reply.created_at) }}</div>
            </div>
          </div>
        </div>

        <v-alert
          v-if="displayNote.is_closed"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-4 rounded-lg"
        >
          {{ t('parent.notes.threadClosed') }}
        </v-alert>

        <div v-else-if="displayNote.can_reply" class="mt-4">
          <v-textarea
            v-model="replyBody"
            :label="t('parent.notes.yourReply')"
            variant="outlined"
            rows="3"
            auto-grow
            rounded="lg"
            hide-details
            class="mb-2"
          />
          <v-btn
            class="btn-glow"
            size="small"
            rounded="lg"
            :loading="saving"
            :disabled="!replyBody.trim()"
            prepend-icon="mdi-reply"
            @click="submitReply"
          >
            {{ t('parent.notes.sendReply') }}
          </v-btn>
        </div>
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'
import ParentNoteCard from './ParentNoteCard.vue'
import {
  PARENT_NOTE_PRIORITY_COLORS,
  PARENT_NOTE_PRIORITY_ICONS,
  PARENT_NOTE_STATUS_COLORS,
} from '../../constants/parentNoteMeta.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  note: { type: Object, required: true },
  role: { type: String, required: true, validator: (v) => ['parent', 'teacher'].includes(v) },
  studentId: { type: Number, default: null },
  loadThread: { type: Function, required: true },
  onReply: { type: Function, required: true },
  onUpdateReply: { type: Function, required: true },
  onDeleteReply: { type: Function, required: true },
})

const emit = defineEmits(['updated', 'error'])

const { t, locale } = useI18n()
const { noteStatus, notePriority } = useLocalizedLabels()

const expanded = ref(false)
const loadingThread = ref(false)
const threadNote = ref(null)
const replyBody = ref('')
const saving = ref(false)
const editingReplyId = ref(null)
const editReplyBody = ref('')

const displayNote = computed(() => threadNote.value || props.note)
const threadReplies = computed(() => displayNote.value?.replies || [])
const statusColor = computed(() => PARENT_NOTE_STATUS_COLORS[displayNote.value?.status] || 'primary')
const priorityColor = computed(() => PARENT_NOTE_PRIORITY_COLORS[displayNote.value?.priority] || 'info')
const priorityIcon = computed(() => PARENT_NOTE_PRIORITY_ICONS[displayNote.value?.priority] || 'mdi-minus')

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

function formatDate(iso) {
  if (!iso) return t('parent.common.emDash')
  try {
    return new Intl.DateTimeFormat(dateLocale(), { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

async function toggleExpand() {
  expanded.value = !expanded.value
  if (expanded.value && !threadNote.value?.replies?.length && props.note.reply_count > 0) {
    await refreshThread()
  }
  if (expanded.value && !threadNote.value) {
    await refreshThread()
  }
}

async function refreshThread() {
  loadingThread.value = true
  try {
    threadNote.value = await props.loadThread(props.note.id)
    emit('updated', threadNote.value)
  } catch (e) {
    emit('error', getErrorMessage(e, t('parent.notes.errors.loadThread')))
  } finally {
    loadingThread.value = false
  }
}

async function submitReply() {
  const text = replyBody.value.trim()
  if (!text) return
  saving.value = true
  try {
    threadNote.value = await props.onReply(props.note.id, text)
    replyBody.value = ''
    emit('updated', threadNote.value)
  } catch (e) {
    emit('error', getErrorMessage(e, t('parent.notes.errors.sendReply')))
  } finally {
    saving.value = false
  }
}

function startEditReply(reply) {
  editingReplyId.value = reply.id
  editReplyBody.value = reply.body
}

function cancelEditReply() {
  editingReplyId.value = null
  editReplyBody.value = ''
}

async function saveEditReply(reply) {
  const text = editReplyBody.value.trim()
  if (!text) return
  saving.value = true
  try {
    threadNote.value = await props.onUpdateReply(props.note.id, reply.id, text)
    cancelEditReply()
    emit('updated', threadNote.value)
  } catch (e) {
    emit('error', getErrorMessage(e, t('parent.notes.errors.editReply')))
  } finally {
    saving.value = false
  }
}

async function removeReply(reply) {
  if (!window.confirm(t('parent.notes.deleteReplyConfirm'))) return
  saving.value = true
  try {
    threadNote.value = await props.onDeleteReply(props.note.id, reply.id)
    emit('updated', threadNote.value)
  } catch (e) {
    emit('error', getErrorMessage(e, t('parent.notes.errors.deleteReply')))
  } finally {
    saving.value = false
  }
}

watch(
  () => props.note,
  (n) => {
    if (threadNote.value?.id === n?.id) {
      threadNote.value = { ...threadNote.value, ...n }
    }
  },
  { deep: true },
)
</script>

<style scoped>
.thread-panel {
  background: rgba(12, 18, 38, 0.92);
  border: 1px solid rgba(124, 108, 240, 0.15);
}

.thread-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.thread-message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.thread-message--parent {
  flex-direction: row-reverse;
}

.thread-message--parent .thread-message__bubble {
  background: rgba(34, 211, 238, 0.1);
  border-color: rgba(34, 211, 238, 0.25);
}

.thread-message--teacher .thread-message__bubble,
.thread-message--root .thread-message__bubble {
  background: rgba(124, 108, 240, 0.12);
  border-color: rgba(124, 108, 240, 0.25);
}

.thread-message__badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 108, 240, 0.15);
  flex-shrink: 0;
}

.thread-message__bubble {
  flex: 1;
  min-width: 0;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid transparent;
}

.thread-message__author {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--em-cyan);
  margin-bottom: 4px;
}

.thread-message__body {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #f0f3fa;
  white-space: pre-wrap;
  word-break: break-word;
}

.thread-message__time {
  font-size: 0.7rem;
  color: var(--em-text-muted);
  margin-top: 6px;
}
</style>
