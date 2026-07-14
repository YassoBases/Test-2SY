<template>

  <div class="chat-panel d-flex flex-column h-100">

    <header class="chat-panel__header">

      <TeacherAvatar

        :name="teacherName"

        :image-url="teacherImageUrl"

        :size="36"

        class="flex-shrink-0"

      />

      <div class="chat-panel__header-text">

        <p class="chat-panel__name">{{ displayTeacherName }}</p>

        <p class="chat-panel__hint">{{ t('student.chat.headerHint') }}</p>

      </div>

      <v-tooltip :text="t('student.chat.clear.tooltip')" location="bottom">

        <template #activator="{ props: tooltipProps }">

          <v-btn

            v-bind="tooltipProps"

            icon="mdi-broom"

            size="x-small"

            variant="text"

            color="medium-emphasis"

            :disabled="clearDisabled || isTyping"

            :loading="clearLoading"

            :aria-label="t('student.chat.clear.aria')"

            @click="$emit('clear')"

          />

        </template>

      </v-tooltip>

    </header>



    <div v-if="statusNotice" class="chat-panel__notice">

      <v-progress-circular

        v-if="statusLoading"

        indeterminate

        size="12"

        width="2"

        color="secondary"

      />

      <v-icon v-else-if="statusError" size="14" color="error">mdi-alert-circle-outline</v-icon>

      <v-icon v-else size="14" color="medium-emphasis">mdi-clock-outline</v-icon>

      <span>{{ statusNotice }}</span>

    </div>



    <div

      v-if="!voiceTtsAvailable && voiceTtsMessage"

      class="chat-panel__notice chat-panel__notice--muted"

    >

      <v-icon size="14">mdi-volume-off</v-icon>

      <span>{{ voiceTtsMessage }}</span>

    </div>



    <div ref="messagesEl" class="chat-panel__messages chat-scroll">

      <TransitionGroup name="chat-msg">

        <ChatBubble

          v-for="msg in messages"

          :key="msg.id"

          :message="msg"

          :teacher-name="teacherName"

          :teacher-image-url="teacherImageUrl"

          @reveal="scrollToBottom"

        />

      </TransitionGroup>

      <TypingIndicator

        v-if="isTyping"

        :teacher-name="teacherName"

        :teacher-image-url="teacherImageUrl"

      />

    </div>



    <div ref="footerEl" class="chat-panel__footer">

      <ChatInput

        ref="chatInputRef"

        :model-value="modelValue"

        :loading="isTyping"

        :voice-loading="isTyping"

        :disabled="sendDisabled"

        :placeholder="sendDisabled ? t('student.chat.input.waitForLesson') : inputPlaceholder"

        @update:model-value="$emit('update:modelValue', $event)"

        @send="$emit('send')"

        @voice="$emit('voice', $event)"

      />

    </div>

  </div>

</template>



<script setup>

import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import ChatBubble from './ChatBubble.vue'

import ChatInput from './ChatInput.vue'

import TypingIndicator from './TypingIndicator.vue'

import TeacherAvatar from '../onboarding/TeacherAvatar.vue'

import '../../assets/styles/chat-experience.css'

const { t } = useI18n()


const props = defineProps({

  messages: { type: Array, required: true },

  modelValue: { type: String, default: '' },

  isTyping: { type: Boolean, default: false },

  teacherName: { type: String, default: '' },

  teacherImageUrl: { type: String, default: null },

  placeholder: { type: String, default: '' },

  clearDisabled: { type: Boolean, default: false },

  clearLoading: { type: Boolean, default: false },

  sendDisabled: { type: Boolean, default: false },

  voiceTtsAvailable: { type: Boolean, default: true },

  voiceTtsMessage: { type: String, default: '' },

  statusNotice: { type: String, default: '' },

  statusLoading: { type: Boolean, default: false },

  statusError: { type: Boolean, default: false },

})



const displayTeacherName = computed(() => {

  const trimmed = (props.teacherName || '').trim()

  return trimmed || t('student.common.teacher')

})



const inputPlaceholder = computed(() => {

  if (props.placeholder) return props.placeholder

  return t('student.chat.input.placeholder', { teacher: displayTeacherName.value })

})



defineEmits(['update:modelValue', 'send', 'voice', 'clear'])



const messagesEl = ref(null)

const footerEl = ref(null)

const chatInputRef = ref(null)



async function scrollToBottom() {

  await nextTick()

  if (messagesEl.value) {

    messagesEl.value.scrollTop = messagesEl.value.scrollHeight

  }

}



async function focusInput() {

  await nextTick()

  footerEl.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })

  await nextTick()

  chatInputRef.value?.focusInput?.()

}



defineExpose({ scrollToBottom, messagesEl, focusInput })

</script>



<style scoped>

.chat-msg-enter-active {

  transition: all 0.3s cubic-bezier(0.34, 1.2, 0.64, 1);

}



.chat-msg-enter-from {

  opacity: 0;

  transform: translateY(8px);

}

</style>

