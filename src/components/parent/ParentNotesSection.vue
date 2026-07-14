<template>
  <section class="mb-8">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-icon color="primary">mdi-note-text-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.notes.title') }}</h3>
        <v-chip v-if="unreadCount > 0" size="small" color="error" variant="flat">
          {{ t('parent.notes.unread', { n: unreadCount }) }}
        </v-chip>
      </div>
      <div class="d-flex gap-2 flex-wrap">
        <v-select
          v-model="categoryFilter"
          :items="categoryItems"
          item-title="label"
          item-value="value"
          :label="t('parent.notes.category')"
          density="compact"
          variant="outlined"
          hide-details
          clearable
          rounded="lg"
          style="min-width: 140px"
        />
        <v-btn-toggle v-model="sortOrder" mandatory density="compact" rounded="lg" color="primary">
          <v-btn value="newest" size="small">{{ t('parent.notes.newest') }}</v-btn>
          <v-btn value="oldest" size="small">{{ t('parent.notes.oldest') }}</v-btn>
        </v-btn-toggle>
      </div>
    </div>

    <v-card class="glass-card glass-card--solid glass-card--elevated pa-4 pa-md-5" variant="flat">
      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3">{{ error }}</v-alert>
      <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-3" />

      <template v-else>
        <ParentNoteThread
          v-for="note in notes"
          :key="note.id"
          :note="note"
          role="parent"
          :student-id="studentId"
          :load-thread="loadNoteThread"
          :on-reply="onReply"
          :on-update-reply="onUpdateReply"
          :on-delete-reply="onDeleteReply"
          @updated="onNoteUpdated"
          @error="onThreadError"
        >
          <template #chips>
            <v-chip
              v-if="!note.is_read_by_viewer"
              size="x-small"
              color="error"
              variant="flat"
            >
              {{ t('parent.notes.new') }}
            </v-chip>
          </template>
          <template #actions>
            <v-btn
              v-if="!note.is_read_by_viewer"
              size="small"
              class="btn-glow flex-shrink-0"
              rounded="lg"
              :loading="markingId === note.id"
              @click="markRead(note)"
            >
              <v-icon start>mdi-check</v-icon>
              {{ t('parent.notes.markRead') }}
            </v-btn>
          </template>
        </ParentNoteThread>

        <p v-if="!notes.length" class="text-caption text-medium-emphasis text-center py-6">
          {{ t('parent.notes.empty') }}
        </p>
      </template>
    </v-card>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'
import ParentNoteThread from './ParentNoteThread.vue'
import {
  acknowledgeParentNote,
  deleteParentNoteReply,
  fetchParentNote,
  fetchParentNoteCategories,
  fetchParentNotes,
  fetchParentNotesUnreadCount,
  replyParentNote,
  updateParentNoteReply,
} from '../../api/parentNotes.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  studentId: { type: Number, default: null },
})

const { t } = useI18n()
const { noteCategory } = useLocalizedLabels()

const loading = ref(true)
const error = ref('')
const notes = ref([])
const unreadCount = ref(0)
const categoryFilter = ref(null)
const sortOrder = ref('newest')
const markingId = ref(null)
const categories = ref([])

const categoryItems = computed(() => [
  { value: null, label: t('parent.notes.all') },
  ...categories.value.map((c) => ({
    value: c.value,
    label: noteCategory(c.value, c.label_ar),
  })),
])

function onThreadError(msg) {
  error.value = msg
}

function onNoteUpdated(updated) {
  notes.value = notes.value.map((n) => (n.id === updated.id ? updated : n))
  if (!updated.is_read_by_viewer) return
  loadUnread()
}

async function loadNoteThread(noteId) {
  return fetchParentNote(noteId)
}

async function onReply(noteId, body) {
  return replyParentNote(noteId, body)
}

async function onUpdateReply(noteId, replyId, body) {
  return updateParentNoteReply(noteId, replyId, body)
}

async function onDeleteReply(noteId, replyId) {
  return deleteParentNoteReply(noteId, replyId)
}

async function loadUnread() {
  if (!props.studentId) return
  try {
    const data = await fetchParentNotesUnreadCount(props.studentId)
    unreadCount.value = data.unread_count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

async function load() {
  if (!props.studentId) return
  loading.value = true
  error.value = ''
  try {
    const params = { student_id: props.studentId, sort: sortOrder.value }
    if (categoryFilter.value) params.category = categoryFilter.value
    const data = await fetchParentNotes(params)
    notes.value = data.notes || []
    unreadCount.value = data.unread_count ?? 0
  } catch (e) {
    error.value = getErrorMessage(e, t('parent.notes.errors.loadNotes'))
    notes.value = []
  } finally {
    loading.value = false
  }
}

async function markRead(note) {
  markingId.value = note.id
  try {
    const updated = await acknowledgeParentNote(note.id)
    onNoteUpdated(updated)
  } catch (e) {
    error.value = getErrorMessage(e, t('parent.notes.errors.markRead'))
  } finally {
    markingId.value = null
  }
}

watch([() => props.studentId, categoryFilter, sortOrder], () => {
  load()
  loadUnread()
})

onMounted(async () => {
  try {
    categories.value = await fetchParentNoteCategories()
  } catch {
    categories.value = []
  }
  await load()
})
</script>
