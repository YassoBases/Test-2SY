import { nextTick, ref } from 'vue'
import { sendChatApi, sendVoiceChatApi, fetchStudentLesson } from '../api/student.js'
import { getErrorMessage, isTimeoutError } from '../api/client.js'
import { formatTimeArabic } from '../utils/format.js'
import { isApiMode } from '../utils/session.js'

export function useAiChat(initialMessages = [], responsePool = []) {
  const messages = ref([...initialMessages])
  const chatInput = ref('')
  const isTyping = ref(false)
  const chatContainer = ref(null)
  const aiResponses = ref([...responsePool])
  const lessonId = ref(null)
  const voiceTtsAvailable = ref(true)
  const voiceTtsMessage = ref('')

  function applyVoiceTtsStatus(data = {}) {
    if (typeof data.voiceTtsAvailable === 'boolean') {
      voiceTtsAvailable.value = data.voiceTtsAvailable
    }
    voiceTtsMessage.value = data.voiceTtsMessage || ''
  }

  function setVoiceTtsStatus(available, message = '') {
    voiceTtsAvailable.value = available
    voiceTtsMessage.value = message || ''
  }

  function mapApiMessages(apiMessages = [], { animateLast = false } = {}) {
    const mapped = apiMessages.map((m) => ({
      id: m.id,
      role: m.role,
      text: m.text,
      time: m.time || formatTimeArabic(),
      audioUrl: m.audioUrl || m.audio_url || null,
      sources: m.sources || [],
      visualElement: m.visualElement || m.visual_element || null,
    }))
    const last = mapped[mapped.length - 1]
    if (animateLast && last?.role === 'ai') {
      last.typewriter = true
    }
    return mapped
  }

  async function syncMessagesFromServer({ animateLast = false } = {}) {
    if (!lessonId.value) return false
    const data = await fetchStudentLesson(lessonId.value)
    applyVoiceTtsStatus(data)
    messages.value = mapApiMessages(data.chatMessages || [], { animateLast })
    return true
  }

  async function pollForAudio(messageId) {
    if (!lessonId.value || !messageId || !voiceTtsAvailable.value) return
    const maxAttempts = 15
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      await new Promise((r) => setTimeout(r, 4000))
      const target = messages.value.find((m) => m.id === messageId)
      if (!target || target.audioUrl) return
      try {
        const data = await fetchStudentLesson(lessonId.value)
        applyVoiceTtsStatus(data)
        const updated = (data.chatMessages || []).find((m) => m.id === messageId)
        const audioUrl = updated?.audioUrl || updated?.audio_url
        if (audioUrl) {
          const idx = messages.value.findIndex((m) => m.id === messageId)
          if (idx !== -1) {
            messages.value[idx] = { ...messages.value[idx], audioUrl }
          }
          return
        }
      } catch {
        return
      }
    }
  }

  function pickAiResponse() {
    const pool = aiResponses.value
    if (!pool.length) {
      return 'سؤال ممتاز! خليني أشرحلك بطريقة أبسط بنفس أسلوب معلمك...'
    }
    return pool[Math.floor(Math.random() * pool.length)]
  }

  async function scrollToBottom() {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }

  function setLessonId(id) {
    lessonId.value = id
  }

  async function sendMessage() {
    const text = chatInput.value.trim()
    if (!text || isTyping.value) return

    messages.value.push({
      id: Date.now(),
      role: 'student',
      text,
      time: formatTimeArabic(),
    })
    chatInput.value = ''
    scrollToBottom()
    isTyping.value = true

    try {
      if (isApiMode() && lessonId.value) {
        const data = await sendChatApi({ lessonId: lessonId.value, message: text })
        applyVoiceTtsStatus(data)
        messages.value = mapApiMessages(data.messages, { animateLast: true })
        const last = messages.value[messages.value.length - 1]
        if (last?.role === 'ai' && !last.audioUrl && voiceTtsAvailable.value) pollForAudio(last.id)
      } else {
        await new Promise((r) => setTimeout(r, 1200 + Math.random() * 800))
        messages.value.push({
          id: Date.now() + 1,
          role: 'ai',
          text: pickAiResponse(),
          time: formatTimeArabic(),
        })
      }
    } catch (err) {
      const timedOut = isTimeoutError(err)
      if (timedOut && lessonId.value) {
        try {
          await syncMessagesFromServer({ animateLast: true })
          const last = messages.value[messages.value.length - 1]
          if (last?.role === 'ai' && !last.audioUrl && voiceTtsAvailable.value) pollForAudio(last.id)
          return
        } catch {
          // fall through
        }
      }
      messages.value.push({
        id: Date.now() + 1,
        role: 'ai',
        text: getErrorMessage(
          err,
          timedOut
            ? 'لا يزال الرد قيد التجهيز — حدّث الدرس أو حاول بعد قليل.'
            : 'تعذر الاتصال بالمعلّم الذكي — حاول مرة أخرى',
        ),
        time: formatTimeArabic(),
      })
    } finally {
      isTyping.value = false
      scrollToBottom()
    }
  }

  async function sendVoiceMessage(blob) {
    if (!blob || isTyping.value) return

    if (!isApiMode() || !lessonId.value) {
      messages.value.push({
        id: Date.now(),
        role: 'ai',
        text: 'التسجيل الصوتي يحتاج اتصالا بالباك إند.',
        time: formatTimeArabic(),
      })
      return
    }

    isTyping.value = true
    scrollToBottom()
    try {
      const voiceFile = new File([blob], 'student-question.webm', {
        type: blob.type || 'audio/webm',
      })
      const data = await sendVoiceChatApi({ lessonId: lessonId.value, file: voiceFile })
      applyVoiceTtsStatus(data)
      messages.value = mapApiMessages(data.messages, { animateLast: true })
      const last = messages.value[messages.value.length - 1]
      if (last?.role === 'ai' && !last.audioUrl && voiceTtsAvailable.value) pollForAudio(last.id)
    } catch (err) {
      messages.value.push({
        id: Date.now() + 1,
        role: 'ai',
        text: getErrorMessage(err, 'تعذر فهم التسجيل الصوتي. حاول مرة أخرى.'),
        time: formatTimeArabic(),
      })
    } finally {
      isTyping.value = false
      scrollToBottom()
    }
  }

  function loadConversation(initial = [], responses = []) {
    messages.value = [...initial]
    aiResponses.value = [...responses]
    chatInput.value = ''
    isTyping.value = false
  }

  return {
    messages,
    chatInput,
    isTyping,
    chatContainer,
    voiceTtsAvailable,
    voiceTtsMessage,
    sendMessage,
    sendVoiceMessage,
    scrollToBottom,
    loadConversation,
    setLessonId,
    setVoiceTtsStatus,
    applyVoiceTtsStatus,
  }
}
