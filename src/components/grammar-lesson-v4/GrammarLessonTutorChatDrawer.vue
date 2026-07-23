<template>
  <div v-if="open" class="grammar-chat" role="dialog" aria-modal="true" aria-label="اسأل المعلّم">
    <button type="button" class="grammar-chat__backdrop" aria-label="إغلاق" @click="$emit('close')" />

    <aside class="grammar-chat__panel" dir="rtl" lang="ar">
      <header class="grammar-chat__header">
        <div>
          <p class="grammar-chat__eyebrow">معلّم القاعدة</p>
          <h3>اسأل المعلّم</h3>
        </div>
        <button type="button" class="grammar-chat__icon" aria-label="إغلاق" @click="$emit('close')">
          ×
        </button>
      </header>

      <div v-if="contextLabel" class="grammar-chat__context">
        عم تسأل عن: <strong>{{ contextLabel }}</strong>
      </div>

      <div class="grammar-chat__quick" aria-label="اقتراحات سريعة">
        <button
          v-for="action in quickActions"
          :key="action"
          type="button"
          :disabled="sending"
          @click="sendQuick(action)"
        >
          {{ action }}
        </button>
      </div>

      <div ref="messagesEl" class="grammar-chat__messages" aria-live="polite">
        <article
          v-for="message in visibleMessages"
          :key="message.id"
          class="grammar-chat__message"
          :class="`grammar-chat__message--${message.role}`"
        >
          <template v-if="message.role === 'user'">
            <p>{{ message.content?.text }}</p>
          </template>

          <template v-else>
            <p v-if="message.content?.reply_ar">{{ message.content.reply_ar }}</p>
            <div v-if="canSpeak(message)" class="grammar-chat__voice-row">
              <button
                type="button"
                class="grammar-chat__voice"
                :class="{ 'grammar-chat__voice--playing': playingMessageId === message.id }"
                :disabled="audioBusyMessageId === message.id"
                @click="toggleMessageAudio(message)"
              >
                <span class="grammar-chat__voice-icon">{{ playingMessageId === message.id ? '■' : '▶' }}</span>
                <span>
                  {{
                    audioBusyMessageId === message.id
                      ? 'عم نجهّز الصوت...'
                      : playingMessageId === message.id
                        ? 'إيقاف الصوت'
                        : 'استمع للشرح'
                  }}
                </span>
              </button>
              <small v-if="audioErrors[message.id]" class="grammar-chat__voice-error">
                تعذّر تشغيل الصوت الآن.
              </small>
            </div>
            <div v-if="message.content?.english_examples?.length" class="grammar-chat__examples">
              <p v-for="example in message.content.english_examples" :key="example" dir="ltr" lang="en">
                {{ example }}
              </p>
            </div>
            <div v-if="message.content?.correction" class="grammar-chat__correction">
              <p v-if="message.content.correction.original" dir="ltr" lang="en">
                {{ message.content.correction.original }}
              </p>
              <p v-if="message.content.correction.corrected" dir="ltr" lang="en">
                {{ message.content.correction.corrected }}
              </p>
              <small v-if="message.content.correction.reason_ar">{{ message.content.correction.reason_ar }}</small>
            </div>
            <p v-if="message.content?.hint" class="grammar-chat__hint">{{ message.content.hint }}</p>
            <div v-if="message.content?.mini_question" class="grammar-chat__mini">
              <strong>تدريب صغير</strong>
              <p>{{ message.content.mini_question.prompt_ar || message.content.mini_question.english_prompt }}</p>
              <div v-if="message.content.mini_question.options?.length" class="grammar-chat__mini-options">
                <span v-for="option in message.content.mini_question.options" :key="option" dir="ltr" lang="en">
                  {{ option }}
                </span>
              </div>
            </div>
          </template>
        </article>

        <article v-if="sending" class="grammar-chat__message grammar-chat__message--assistant">
          <p>عم حضّر جواب قصير...</p>
        </article>
      </div>

      <div v-if="error" class="grammar-chat__error" role="alert">
        <span>{{ error }}</span>
        <button v-if="lastFailedDraft" type="button" @click="retryLast">إعادة المحاولة</button>
      </div>

      <footer class="grammar-chat__composer">
        <textarea
          v-model="draft"
          rows="2"
          :maxlength="800"
          :disabled="sending || loading"
          placeholder="اكتب سؤالك أو جملة إنجليزية..."
          @keydown.ctrl.enter.prevent="sendDraft"
        />
        <div class="grammar-chat__composer-actions">
          <button type="button" class="grammar-chat__reset" :disabled="sending || !sessionId" @click="resetSession">
            محادثة جديدة
          </button>
          <button type="button" class="grammar-chat__send" :disabled="!canSend" @click="sendDraft">
            {{ sending ? 'جار الإرسال...' : 'إرسال' }}
          </button>
        </div>
      </footer>
    </aside>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import {
  closeGrammarLessonChatSession,
  closeGrammarLessonPreviewChatSession,
  createGrammarLessonChatSession,
  createGrammarLessonPreviewChatSession,
  sendGrammarLessonChatMessage,
  sendGrammarLessonPreviewChatMessage,
  synthesizeGrammarLessonChatAudio,
  synthesizeGrammarLessonPreviewChatAudio,
} from '../../api/grammar.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  revisionId: { type: String, default: '' },
  context: { type: Object, default: null },
  previewMode: { type: Boolean, default: false },
})

defineEmits(['close'])

const quickActions = [
  'اشرحها أبسط',
  'عطيني مثال',
  'صحّح جملتي',
  'اختبرني بسؤال',
  'شو الفرق عن العربي؟',
]

const sessionId = ref('')
const messages = ref([])
const draft = ref('')
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const lastFailedDraft = ref('')
const messagesEl = ref(null)
const audioBusyMessageId = ref('')
const playingMessageId = ref('')
const audioUrls = ref({})
const audioErrors = ref({})
let currentAudio = null

const contextLabel = computed(() => props.context?.title || props.context?.label || '')
const visibleMessages = computed(() =>
  messages.value.filter((message) => message?.role === 'user' || message?.role === 'assistant'),
)
const canSend = computed(() => !!draft.value.trim() && !sending.value && !loading.value && !!props.revisionId)
const chatApi = computed(() => ({
  create: props.previewMode ? createGrammarLessonPreviewChatSession : createGrammarLessonChatSession,
  send: props.previewMode ? sendGrammarLessonPreviewChatMessage : sendGrammarLessonChatMessage,
  close: props.previewMode ? closeGrammarLessonPreviewChatSession : closeGrammarLessonChatSession,
  audio: props.previewMode ? synthesizeGrammarLessonPreviewChatAudio : synthesizeGrammarLessonChatAudio,
}))

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) await ensureSession()
    else stopCurrentAudio()
  },
)

watch(
  () => props.revisionId,
  () => {
    stopCurrentAudio()
    sessionId.value = ''
    messages.value = []
    error.value = ''
    audioUrls.value = {}
    audioErrors.value = {}
  },
)

onBeforeUnmount(() => {
  stopCurrentAudio()
})

async function ensureSession() {
  if (sessionId.value || loading.value || !props.revisionId) return
  loading.value = true
  error.value = ''
  try {
    const data = await chatApi.value.create(props.revisionId)
    applySession(data)
  } catch {
    error.value = 'تعذّر فتح الشات الآن. جرّب مرة ثانية.'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

function applySession(data) {
  sessionId.value = data?.session_id || ''
  messages.value = Array.isArray(data?.messages) ? data.messages : []
}

function sendQuick(action) {
  draft.value = action
  sendDraft()
}

async function sendDraft() {
  const text = draft.value.trim()
  if (!text || sending.value) return
  await ensureSession()
  if (!sessionId.value) return
  draft.value = ''
  sending.value = true
  error.value = ''
  lastFailedDraft.value = ''
  try {
    const data = await chatApi.value.send(sessionId.value, {
      revision_id: props.revisionId,
      message: text,
      section_key: props.context?.section_key || '',
      block_context: props.context || null,
    })
    messages.value = Array.isArray(data?.messages) ? data.messages : [
      ...messages.value,
      data.user_message,
      data.assistant_message,
    ].filter(Boolean)
    if (data?.assistant_message) {
      void playMessageAudio(data.assistant_message, { silentErrors: true })
    }
  } catch {
    draft.value = text
    lastFailedDraft.value = text
    error.value = 'ما قدرنا نرسل السؤال. جرّب مرة ثانية.'
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}

async function retryLast() {
  if (!lastFailedDraft.value) return
  draft.value = lastFailedDraft.value
  await sendDraft()
}

async function resetSession() {
  if (!sessionId.value || sending.value) return
  stopCurrentAudio()
  try {
    await chatApi.value.close(sessionId.value, props.revisionId)
  } catch {
    /* chat reset is best-effort */
  }
  sessionId.value = ''
  messages.value = []
  await ensureSession()
}

function canSpeak(message) {
  return message?.role === 'assistant' && !!String(message?.content?.reply_ar || '').trim()
}

async function toggleMessageAudio(message) {
  if (playingMessageId.value === message.id) {
    stopCurrentAudio()
    return
  }
  await playMessageAudio(message)
}

async function playMessageAudio(message, { silentErrors = false } = {}) {
  if (!canSpeak(message) || !sessionId.value || !props.revisionId) return
  audioErrors.value = { ...audioErrors.value, [message.id]: false }
  try {
    const url = await ensureMessageAudioUrl(message)
    if (!url) return
    stopCurrentAudio()
    const audio = new Audio(url)
    currentAudio = audio
    playingMessageId.value = message.id
    audio.onended = () => {
      if (currentAudio === audio) playingMessageId.value = ''
    }
    audio.onerror = () => {
      if (currentAudio === audio) {
        playingMessageId.value = ''
        audioErrors.value = { ...audioErrors.value, [message.id]: true }
      }
    }
    await audio.play()
  } catch {
    playingMessageId.value = ''
    if (!silentErrors) {
      audioErrors.value = { ...audioErrors.value, [message.id]: true }
    }
  }
}

async function ensureMessageAudioUrl(message) {
  if (audioUrls.value[message.id]) return audioUrls.value[message.id]
  audioBusyMessageId.value = message.id
  try {
    const data = await chatApi.value.audio(sessionId.value, message.id, {
      revision_id: props.revisionId,
    })
    const url = data?.audio_url || ''
    if (url) {
      audioUrls.value = { ...audioUrls.value, [message.id]: url }
    }
    return url
  } finally {
    audioBusyMessageId.value = ''
  }
}

function stopCurrentAudio() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
  playingMessageId.value = ''
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}
</script>

<style scoped>
.grammar-chat {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: flex;
  justify-content: flex-end;
}

.grammar-chat__backdrop {
  position: absolute;
  inset: 0;
  border: 0;
  background: rgba(35, 29, 21, 0.28);
}

.grammar-chat__panel {
  position: relative;
  width: min(440px, 100%);
  height: 100%;
  display: grid;
  grid-template-rows: auto auto auto 1fr auto auto;
  gap: 12px;
  padding: 18px;
  background: #fffdf8;
  border-inline-start: 1px solid rgba(63, 49, 34, 0.14);
  box-shadow: -18px 0 45px rgba(80, 62, 40, 0.14);
  color: #242018;
}

.grammar-chat__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.grammar-chat__eyebrow,
.grammar-chat__header h3 {
  margin: 0;
}

.grammar-chat__eyebrow {
  color: #41685a;
  font-weight: 800;
  font-size: 0.78rem;
}

.grammar-chat__header h3 {
  font-size: 1.45rem;
  letter-spacing: 0;
}

.grammar-chat__icon {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  border: 1px solid rgba(63, 49, 34, 0.14);
  background: #fbf6ed;
  color: #242018;
  font-size: 1.4rem;
  cursor: pointer;
}

.grammar-chat__context,
.grammar-chat__error,
.grammar-chat__hint {
  border-radius: 10px;
  padding: 10px 12px;
  background: #fbf6ed;
  color: #6f655b;
  line-height: 1.55;
}

.grammar-chat__quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.grammar-chat__quick button,
.grammar-chat__reset {
  border: 1px solid rgba(65, 104, 90, 0.22);
  border-radius: 999px;
  background: rgba(65, 104, 90, 0.09);
  color: #41685a;
  padding: 7px 10px;
  font-weight: 800;
  cursor: pointer;
}

.grammar-chat__messages {
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-inline-end: 4px;
}

.grammar-chat__message {
  max-width: 92%;
  border: 1px solid rgba(63, 49, 34, 0.12);
  border-radius: 14px;
  padding: 12px 14px;
  background: #ffffff;
  line-height: 1.65;
}

.grammar-chat__message p {
  margin: 0;
}

.grammar-chat__voice-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-block-start: 10px;
}

.grammar-chat__voice {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid rgba(65, 104, 90, 0.24);
  border-radius: 999px;
  background: #eef4ee;
  color: #41685a;
  padding: 7px 11px;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 900;
  cursor: pointer;
}

.grammar-chat__voice:hover:not(:disabled),
.grammar-chat__voice--playing {
  border-color: rgba(65, 104, 90, 0.42);
  background: #dfeae2;
}

.grammar-chat__voice:disabled {
  cursor: wait;
  opacity: 0.76;
}

.grammar-chat__voice-icon {
  display: inline-grid;
  place-items: center;
  width: 18px;
  height: 18px;
  font-size: 0.68rem;
  direction: ltr;
}

.grammar-chat__voice-error {
  color: #8e3d35;
  font-weight: 800;
}

.grammar-chat__message--user {
  align-self: flex-start;
  background: #41685a;
  color: #ffffff;
}

.grammar-chat__message--assistant {
  align-self: flex-end;
}

.grammar-chat__examples,
.grammar-chat__correction,
.grammar-chat__mini {
  display: grid;
  gap: 7px;
  margin-block-start: 10px;
}

.grammar-chat__examples p,
.grammar-chat__correction p,
.grammar-chat__mini-options span {
  border-radius: 8px;
  background: #fbf6ed;
  padding: 8px 10px;
  font-weight: 800;
  text-align: left;
  unicode-bidi: isolate;
}

.grammar-chat__correction small {
  color: #6f655b;
}

.grammar-chat__mini-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.grammar-chat__error {
  background: #fdecea;
  color: #8e3d35;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.grammar-chat__error button {
  border: 0;
  border-radius: 999px;
  padding: 6px 9px;
  background: #8e3d35;
  color: #fff;
  cursor: pointer;
}

.grammar-chat__composer {
  display: grid;
  gap: 10px;
}

.grammar-chat__composer textarea {
  width: 100%;
  resize: vertical;
  min-height: 64px;
  border: 1px solid rgba(63, 49, 34, 0.16);
  border-radius: 12px;
  padding: 11px 12px;
  background: #ffffff;
  color: #242018;
  font: inherit;
}

.grammar-chat__composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.grammar-chat__send {
  border: 0;
  border-radius: 999px;
  background: #41685a;
  color: #ffffff;
  padding: 10px 18px;
  font-weight: 900;
  cursor: pointer;
}

.grammar-chat__send:disabled,
.grammar-chat__reset:disabled,
.grammar-chat__quick button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

@media (max-width: 720px) {
  .grammar-chat {
    align-items: flex-end;
  }

  .grammar-chat__panel {
    width: 100%;
    height: min(86vh, 720px);
    border-radius: 18px 18px 0 0;
    border-inline-start: 0;
  }
}
</style>
