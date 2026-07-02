<template>
  <v-expansion-panels v-if="isGroup" class="mb-0" variant="accordion">
    <v-expansion-panel>
      <v-expansion-panel-title class="text-caption font-weight-bold">
        {{ t('messages.groupParticipants.title', { count: thread.participants?.length || 0 }) }}
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <div class="d-flex flex-wrap gap-1 mb-3">
          <v-chip
            v-for="p in thread.participants"
            :key="p.user_id"
            size="small"
            variant="tonal"
            :closable="isTeacher && p.role === 'parent'"
            @click:close="$emit('remove-parent', p.user_id)"
          >
            {{ p.display_name || p.name }} — {{ p.role_label || p.role }}
          </v-chip>
        </div>
        <v-select
          v-model="selectedParent"
          :items="parentOptions"
          item-title="label"
          item-value="id"
          :label="t('messages.groupParticipants.addParent')"
          density="compact"
          variant="outlined"
          hide-details
          clearable
        />
        <v-btn
          class="mt-2"
          size="small"
          block
          variant="tonal"
          :disabled="!selectedParent"
          @click="addParent"
        >
          {{ t('messages.groupParticipants.add') }}
        </v-btn>
        <v-btn
          v-if="!hasStudent"
          class="mt-2"
          size="small"
          block
          color="primary"
          variant="tonal"
          @click="$emit('add-student')"
        >
          {{ t('messages.groupParticipants.addStudent') }}
        </v-btn>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  thread: { type: Object, required: true },
  contacts: { type: Object, default: () => ({ parents: [] }) },
  isTeacher: { type: Boolean, default: false },
})

const emit = defineEmits(['add-parent', 'remove-parent', 'add-student'])

const { t } = useI18n()

const selectedParent = ref(null)

const isGroup = computed(() => props.thread?.thread_type === 'teacher_student_parent')
const hasStudent = computed(() =>
  (props.thread?.participants || []).some((p) => p.role === 'student'),
)

const parentOptions = computed(() => {
  const inThread = new Set((props.thread?.participants || []).map((p) => p.user_id))
  return (props.contacts?.parents || [])
    .filter((p) => p.student_id === props.thread?.student_id && !inThread.has(p.user_id))
    .map((p) => ({ id: p.user_id, label: p.name }))
})

function addParent() {
  if (selectedParent.value) {
    emit('add-parent', selectedParent.value)
    selectedParent.value = null
  }
}
</script>
