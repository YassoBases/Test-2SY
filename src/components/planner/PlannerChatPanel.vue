<template>
  <v-card class="planner-chat glass-card d-flex flex-column" variant="flat">
    <div class="pa-4 border-b">
      <div class="d-flex align-center gap-2">
        <v-avatar size="36" class="eduspark-gradient">
          <v-icon color="white" size="20">mdi-calendar-edit</v-icon>
        </v-avatar>
        <div>
          <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('common.planner.aiAssistant') }}</h3>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('common.planner.aiSubtitle') }}</p>
        </div>
      </div>
    </div>

    <div ref="scrollEl" class="chat-messages flex-grow-1 pa-4">
      <div v-if="!messages.length" class="empty-chat text-center pa-6">
        <EduSparkBrandIcon context="empty" class="mb-3" />
        <p class="text-body-2 text-medium-emphasis mb-4">{{ t('common.planner.trySaying') }}</p>
        <v-chip
          v-for="hint in hints"
          :key="hint"
          class="ma-1"
          variant="tonal"
          size="small"
          @click="$emit('send', hint)"
        >
          {{ hint }}
        </v-chip>
      </div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        class="chat-row mb-3"
        :class="msg.role === 'user' ? 'chat-row--user' : 'chat-row--ai'"
      >
        <div class="chat-bubble" :class="msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--ai'">
          <p class="text-body-2 mb-0 chat-content">{{ msg.content }}</p>
        </div>
      </div>

      <div v-if="loading" class="d-flex align-center gap-2 text-medium-emphasis">
        <v-progress-circular indeterminate size="18" width="2" />
        <span class="text-caption">{{ t('common.planner.updatingSchedule') }}</span>
      </div>
    </div>

    <div class="pa-3 border-t">
      <v-textarea
        v-model="draft"
        rows="2"
        auto-grow
        max-rows="4"
        variant="outlined"
        density="compact"
        hide-details
        :placeholder="t('common.planner.inputPlaceholder')"
        class="mb-2"
        @keydown.enter.exact.prevent="submit"
      />
      <v-btn
        block
        color="primary"
        rounded="lg"
        class="btn-glow"
        :loading="loading"
        :disabled="!draft.trim()"
        prepend-icon="mdi-send"
        @click="submit"
      >
        {{ t('common.planner.updatePlan') }}
      </v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['send'])
const { t, tm } = useI18n()

const draft = ref('')
const scrollEl = ref(null)

const hints = computed(() => tm('common.planner.hints'))

function submit() {
  const text = draft.value.trim()
  if (!text) return
  emit('send', text)
  draft.value = ''
}

watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
  },
)
</script>

<style scoped>
.planner-chat {
  min-height: 420px;
  max-height: 640px;
}

.chat-messages {
  overflow-y: auto;
  min-height: 200px;
}

.chat-row--user {
  display: flex;
  justify-content: flex-start;
}

.chat-row--ai {
  display: flex;
  justify-content: flex-end;
}

.chat-bubble {
  max-width: 92%;
  padding: 10px 14px;
  border-radius: 14px;
}

.chat-bubble--user {
  background: rgba(var(--v-theme-primary), 0.15);
  border: 1px solid rgba(var(--v-theme-primary), 0.25);
}

.chat-bubble--ai {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.border-b,
.border-t {
  border-color: rgba(255, 255, 255, 0.08) !important;
}
</style>
