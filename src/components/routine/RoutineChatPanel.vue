<template>
  <v-card class="glass-card pa-4 routine-chat" variant="flat">
    <h3 class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center gap-2">
      <EduSparkBrandIcon context="inline" />
      {{ t('common.routine.editProgram') }}
    </h3>

    <div class="chat-history mb-3" ref="chatEl">
      <div v-if="messages.length === 0" class="routine-chat-empty text-center py-4">
        <EduSparkBrandIcon context="empty" class="mb-3" />
        <p class="text-caption text-medium-emphasis mb-0">{{ t('common.routine.chatHint') }}</p>
      </div>
      <div v-for="msg in messages" :key="msg.id"
        class="msg-bubble mb-2 pa-3 rounded-lg"
        :class="msg.role === 'user' ? 'msg-user' : 'msg-ai'">
        <p class="text-body-2 mb-0" style="white-space:pre-wrap">{{ msg.content }}</p>
      </div>
    </div>

    <div class="d-flex flex-wrap gap-1 mb-3">
      <v-chip v-for="s in suggestions" :key="s" size="x-small" variant="tonal" color="primary"
        class="cursor-pointer" @click="sendMessage(s)">{{ s }}</v-chip>
    </div>

    <div class="d-flex gap-2">
      <v-textarea v-model="input" :rows="2" variant="outlined" density="compact"
        :placeholder="t('common.routine.inputPlaceholder')" auto-grow hide-details
        @keydown.enter.prevent="if(!$event.shiftKey) sendMessage(input)" />
      <v-btn icon color="primary" :loading="loading" @click="sendMessage(input)">
        <v-icon>mdi-send</v-icon>
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { chatWithRoutine, confirmSchedule } from '../../api/routine.js'
import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

const emit = defineEmits(['schedule-update'])

const { t, tm } = useI18n()

const input = ref('')
const loading = ref(false)
const messages = ref([])
const chatEl = ref(null)

const suggestions = computed(() => tm('common.routine.hints'))

async function sendMessage(text) {
  if (!text?.trim()) return
  const msg = text.trim()
  input.value = ''
  messages.value.push({ id: Date.now(), role: 'user', content: msg })
  await scrollDown()
  loading.value = true

  try {
    const { data } = await chatWithRoutine(msg)
    messages.value.push({ id: Date.now() + 1, role: 'ai', content: data.reply })

    if (data.schedule && data.ready_to_confirm) {
      await confirmSchedule(data.schedule)
      emit('schedule-update', data.schedule)
    }
  } catch {
    messages.value.push({ id: Date.now() + 1, role: 'ai', content: t('common.routine.errorRetry') })
  } finally {
    loading.value = false
    await scrollDown()
  }
}

async function scrollDown() {
  await nextTick()
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}
</script>

<style scoped>
.routine-chat { height: 100%; }
.chat-history { max-height: 350px; overflow-y: auto; }
.msg-bubble { max-width: 100%; }
.msg-user { background: rgba(124,108,240,0.15); border: 1px solid rgba(124,108,240,0.2); margin-left: 1rem; }
.msg-ai { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); margin-right: 1rem; }
.cursor-pointer { cursor: pointer; }
</style>
