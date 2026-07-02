<template>
  <v-dialog :model-value="modelValue" max-width="520" persistent @update:model-value="$emit('update:modelValue', $event)">
    <v-card class="pa-5 rounded-xl" dir="rtl">
      <v-card-title class="px-0">{{ t('messages.newDialog.title') }}</v-card-title>
      <v-select
        v-model="studentId"
        :items="students"
        item-title="name"
        item-value="user_id"
        :label="t('messages.newDialog.studentLabel')"
        variant="outlined"
        rounded="lg"
        class="mb-3"
      />
      <v-checkbox
        v-model="includeStudent"
        :label="t('messages.newDialog.addStudentLabel')"
        density="compact"
        hide-details
        class="mb-2"
      />
      <v-select
        v-model="parentIds"
        :items="filteredParents"
        item-title="label"
        item-value="user_id"
        :label="t('messages.newDialog.parentsLabel')"
        variant="outlined"
        rounded="lg"
        multiple
        chips
        clearable
        class="mb-3"
      />
      <v-text-field v-model="title" :label="t('messages.newDialog.customTitleLabel')" variant="outlined" rounded="lg" />
      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-3">{{ error }}</v-alert>
      <v-card-actions class="px-0 pt-4">
        <v-spacer />
        <v-btn variant="text" :disabled="saving" @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</v-btn>
        <v-btn class="btn-glow" rounded="lg" :loading="saving" @click="create">{{ t('messages.newDialog.create') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { createConversation, fetchMessagingContacts } from '../../api/messages.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'created'])

const { t } = useI18n()

const students = ref([])
const parents = ref([])
const studentId = ref(null)
const parentIds = ref([])
const includeStudent = ref(true)
const title = ref('')
const saving = ref(false)
const error = ref('')

const filteredParents = computed(() => {
  if (!studentId.value) return []
  return parents.value
    .filter((p) => p.student_id === studentId.value)
    .map((p) => ({
      ...p,
      label: t('messages.newDialog.parentOption', { name: p.name, student: p.student_name }),
    }))
})

async function loadContacts() {
  try {
    const data = await fetchMessagingContacts()
    students.value = data.students || []
    parents.value = data.parents || []
    if (students.value.length && !studentId.value) {
      studentId.value = students.value[0].user_id
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.loadContacts'))
  }
}

async function create() {
  if (!studentId.value) {
    error.value = t('messages.newDialog.selectStudentRequired')
    return
  }
  if (!includeStudent.value && !parentIds.value.length) {
    error.value = t('messages.newDialog.selectStudentOrParentRequired')
    return
  }
  saving.value = true
  error.value = ''
  try {
    const thread = await createConversation({
      student_id: studentId.value,
      parent_ids: parentIds.value,
      include_student: includeStudent.value,
      title: title.value.trim() || null,
    })
    emit('created', thread)
    emit('update:modelValue', false)
  } catch (e) {
    error.value = getErrorMessage(e, t('messages.errors.createConversation'))
  } finally {
    saving.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      error.value = ''
      parentIds.value = []
      loadContacts()
    }
  },
)
</script>
