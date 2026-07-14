<template>
  <v-card class="glass-card pa-5 mb-4" variant="flat">
    <h3 class="text-h6 font-weight-bold mb-1">{{ $t('teacher.students.parentContact') }}</h3>
    <p class="text-caption text-medium-emphasis mb-4">{{ $t('teacher.students.parentContactHint') }}</p>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3">{{ error }}</v-alert>

    <template v-if="parents.length">
      <div
        v-for="parent in parents"
        :key="parent.parent_id"
        class="d-flex align-center justify-space-between flex-wrap gap-3 mb-3 pa-3 rounded-lg parent-row"
      >
        <div>
          <div class="text-caption text-medium-emphasis">{{ $t('teacher.labels.parent') }}</div>
          <div class="text-body-1 font-weight-medium">{{ parent.full_name }}</div>
          <div v-if="parent.email" class="text-caption text-medium-emphasis">{{ parent.email }}</div>
        </div>
        <v-btn
          class="btn-glow"
          size="small"
          rounded="lg"
          prepend-icon="mdi-message-text-outline"
          :loading="openingId === parent.parent_id"
          @click="startConversation(parent)"
        >
          {{ $t('teacher.actions.sendMessage') }}
        </v-btn>
      </div>
    </template>
    <p v-else class="text-caption text-medium-emphasis text-center py-4 mb-0">
      {{ $t('teacher.students.noParentLinked') }}
    </p>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useRouter } from 'vue-router'
import { createConversation } from '../../api/messages.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'

const props = defineProps({
  studentId: { type: Number, required: true },
  parents: { type: Array, default: () => [] },
})

const router = useRouter()
const openingId = ref(null)
const error = ref('')

async function startConversation(parent) {
  openingId.value = parent.parent_id
  error.value = ''
  try {
    const thread = await createConversation({
      student_id: props.studentId,
      parent_ids: [parent.parent_id],
      include_student: false,
    })
    const threadId = thread?.id ?? thread?.thread_id
    if (threadId) {
      await router.push({ path: ROUTES.TEACHER_MESSAGES, query: { thread: threadId } })
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.startConversation'))
  } finally {
    openingId.value = null
  }
}
</script>

<style scoped>
.parent-row {
  background: rgba(var(--v-theme-on-surface), 0.04);
}
</style>
