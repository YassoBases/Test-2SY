<template>
  <v-dialog :model-value="modelValue" max-width="440" persistent @update:model-value="$emit('update:modelValue', $event)">
    <v-card class="rounded-xl">
      <v-card-title class="text-h6 font-weight-bold pt-4 px-4 pb-2">
        {{ t('messages.notificationDialog.title') }}
      </v-card-title>
      <v-card-text class="px-4 pb-2">
        <p class="text-caption text-medium-emphasis mb-3">
          {{ t('messages.notificationDialog.hint') }}
        </p>

        <v-checkbox
          v-if="showStudent"
          v-model="selectedStudent"
          hide-details
          density="compact"
          color="primary"
          :label="studentLabel"
          class="mb-1"
        />

        <v-checkbox
          v-for="parent in parents"
          :key="parent.parent_id"
          v-model="selectedParentIds"
          hide-details
          density="compact"
          color="primary"
          :value="parent.parent_id"
          :label="parentCheckboxLabel(parent)"
          class="mb-1"
        />

        <p v-if="!showStudent && !parents.length" class="text-caption text-medium-emphasis mb-0">
          {{ t('messages.notificationDialog.noRecipients') }}
        </p>
      </v-card-text>

      <v-card-actions class="px-4 pb-4 pt-2">
        <v-spacer />
        <v-btn variant="text" rounded="lg" @click="close">{{ t('common.cancel') }}</v-btn>
        <v-btn
          color="primary"
          variant="flat"
          rounded="lg"
          :disabled="!canConfirm"
          @click="confirm"
        >
          {{ t('messages.notificationDialog.continue') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { relationshipLabelAr } from '../../utils/subscriptionStatus.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  studentName: { type: String, default: '' },
  showStudent: { type: Boolean, default: true },
  parents: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const { t } = useI18n()

const selectedStudent = ref(true)
const selectedParentIds = ref([])

const studentLabel = computed(() => {
  if (props.studentName) return t('messages.studentWithName', { name: props.studentName })
  return t('messages.studentOnly')
})

const canConfirm = computed(() => {
  if (selectedStudent.value && props.showStudent) return true
  return selectedParentIds.value.length > 0
})

function parentCheckboxLabel(parent) {
  const rel = relationshipLabelAr(parent.relationship_label)
  return `${parent.full_name} (${rel})`
}

function resetSelection() {
  selectedStudent.value = props.showStudent
  selectedParentIds.value = props.parents.map((p) => p.parent_id)
}

function close() {
  emit('update:modelValue', false)
}

function confirm() {
  emit('confirm', {
    includeStudent: props.showStudent && selectedStudent.value,
    parentIds: [...selectedParentIds.value],
  })
  emit('update:modelValue', false)
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) resetSelection()
  },
)

watch(
  () => props.parents,
  () => {
    if (props.modelValue) resetSelection()
  },
  { deep: true },
)
</script>
