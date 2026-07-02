<template>
  <v-card class="glass-card pa-5" variant="flat">
    <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
      <div>
        <h3 class="text-h6 font-weight-bold mb-0">{{ $t('teacher.parentNotes.title') }}</h3>
        <p class="text-caption text-medium-emphasis mb-0">{{ $t('teacher.parentNotes.subtitle') }}</p>
      </div>
      <v-btn size="small" class="btn-glow" rounded="lg" @click="openDialog()">
        <v-icon start>mdi-plus</v-icon>
        {{ $t('teacher.actions.createParentNote') }}
      </v-btn>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3">{{ error }}</v-alert>
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-3" />

    <template v-else>
      <ParentNoteThread
        v-for="note in notes"
        :key="note.id"
        :note="note"
        role="teacher"
        :student-id="studentId"
        :load-thread="loadNoteThread"
        :on-reply="onReply"
        :on-update-reply="onUpdateReply"
        :on-delete-reply="onDeleteReply"
        @updated="onNoteUpdated"
        @error="onThreadError"
      >
        <template #actions>
          <div v-if="note.can_edit || note.can_close" class="d-flex flex-column align-end gap-1">
            <div v-if="note.can_edit" class="d-flex">
              <v-btn icon size="x-small" variant="text" @click="openDialog(note)">
                <v-icon size="18">mdi-pencil-outline</v-icon>
              </v-btn>
              <v-btn icon size="x-small" variant="text" color="error" @click="confirmDelete(note)">
                <v-icon size="18">mdi-delete-outline</v-icon>
              </v-btn>
            </div>
            <v-btn
              v-if="note.can_close"
              size="x-small"
              variant="tonal"
              color="grey"
              rounded="lg"
              :loading="closingId === note.id"
              @click="closeNote(note)"
            >
              {{ $t('teacher.actions.closeConversation') }}
            </v-btn>
          </div>
        </template>
      </ParentNoteThread>

      <p v-if="!notes.length" class="text-caption text-medium-emphasis text-center py-4">
        {{ $t('teacher.parentNotes.empty') }}
      </p>
    </template>

    <v-dialog v-model="dialog" max-width="520" persistent>
      <v-card class="pa-5 rounded-xl" dir="rtl">
        <v-card-title class="px-0">{{ editing ? $t('teacher.parentNotes.editNoteTitle') : $t('teacher.parentNotes.noteForParent') }}</v-card-title>
        <v-text-field v-model="form.title" :label="$t('teacher.labels.title')" variant="outlined" rounded="lg" class="mb-3" />
        <v-select
          v-model="form.category"
          :items="categories"
          item-title="label_ar"
          item-value="value"
          :label="$t('teacher.labels.category')"
          variant="outlined"
          rounded="lg"
          class="mb-3"
        />
        <v-select
          v-model="form.priority"
          :items="priorities"
          item-title="label_ar"
          item-value="value"
          :label="$t('teacher.labels.priority')"
          variant="outlined"
          rounded="lg"
          class="mb-3"
        />
        <v-textarea
          v-model="form.description"
          :label="$t('teacher.labels.description')"
          variant="outlined"
          rows="4"
          auto-grow
          rounded="lg"
        />
        <v-card-actions class="px-0 pt-2">
          <v-spacer />
          <v-btn variant="text" :disabled="saving" @click="dialog = false">{{ $t('common.cancel') }}</v-btn>
          <v-btn class="btn-glow" :loading="saving" rounded="lg" @click="save">{{ $t('common.save') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import ParentNoteThread from '../parent/ParentNoteThread.vue'
import {
  closeTeacherParentNote,
  createTeacherParentNote,
  deleteTeacherParentNote,
  deleteTeacherParentNoteReply,
  fetchTeacherParentNote,
  fetchTeacherParentNoteCategories,
  fetchTeacherParentNotePriorities,
  fetchTeacherParentNotes,
  replyTeacherParentNote,
  updateTeacherParentNote,
  updateTeacherParentNoteReply,
} from '../../api/parentNotes.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  studentId: { type: Number, required: true },
})

const loading = ref(true)
const error = ref('')
const notes = ref([])
const categories = ref([])
const priorities = ref([])
const dialog = ref(false)
const saving = ref(false)
const closingId = ref(null)
const editing = ref(null)
const form = reactive({ title: '', description: '', category: 'academic', priority: 'medium' })

function onThreadError(msg) {
  error.value = msg
}

function onNoteUpdated(updated) {
  notes.value = notes.value.map((n) => (n.id === updated.id ? updated : n))
}

async function loadNoteThread(noteId) {
  return fetchTeacherParentNote(props.studentId, noteId)
}

async function onReply(noteId, body) {
  return replyTeacherParentNote(props.studentId, noteId, body)
}

async function onUpdateReply(noteId, replyId, body) {
  return updateTeacherParentNoteReply(props.studentId, noteId, replyId, body)
}

async function onDeleteReply(noteId, replyId) {
  return deleteTeacherParentNoteReply(props.studentId, noteId, replyId)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchTeacherParentNotes(props.studentId)
    notes.value = data.notes || []
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadParentNotes'))
    notes.value = []
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  try {
    categories.value = await fetchTeacherParentNoteCategories()
  } catch {
    categories.value = []
  }
  try {
    priorities.value = await fetchTeacherParentNotePriorities()
  } catch {
    priorities.value = [
      { value: 'low', label_ar: t('teacher.parentNotes.priorityLow') },
      { value: 'medium', label_ar: t('teacher.parentNotes.priorityMedium') },
      { value: 'high', label_ar: t('teacher.parentNotes.priorityHigh') },
      { value: 'urgent', label_ar: t('teacher.parentNotes.priorityUrgent') },
    ]
  }
}

function openDialog(note = null) {
  editing.value = note
  form.title = note?.title || ''
  form.description = note?.description || ''
  form.category = note?.category || 'academic'
  form.priority = note?.priority || 'medium'
  dialog.value = true
}

async function save() {
  if (!form.title?.trim() || !form.description?.trim()) {
    error.value = t('teacher.validation.enterTitleDesc')
    return
  }
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      category: form.category,
      priority: form.priority,
    }
    if (editing.value) {
      await updateTeacherParentNote(props.studentId, editing.value.id, payload)
    } else {
      await createTeacherParentNote(props.studentId, payload)
    }
    dialog.value = false
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveNote'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete(note) {
  if (!window.confirm(t('teacher.confirm.deleteNote'))) return
  try {
    await deleteTeacherParentNote(props.studentId, note.id)
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.deleteNote'))
  }
}

async function closeNote(note) {
  if (!window.confirm(t('teacher.parentNotes.closeConfirm'))) return
  closingId.value = note.id
  try {
    const updated = await closeTeacherParentNote(props.studentId, note.id)
    onNoteUpdated(updated)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.closeConversation'))
  } finally {
    closingId.value = null
  }
}

watch(() => props.studentId, load, { immediate: false })
onMounted(async () => {
  await loadMeta()
  await load()
})
</script>
