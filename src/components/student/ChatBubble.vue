<template>
  <div
    class="chat-row d-flex"
    :class="message.role === 'student' ? 'flex-row-reverse' : ''"
  >
    <v-avatar
      v-if="message.role !== 'ai'"
      class="avatar-student flex-shrink-0"
      size="34"
    >
      <v-icon size="18" color="white">mdi-account</v-icon>
    </v-avatar>
    <LessonChatTeacherAvatar
      v-else
      :name="teacherName"
      :image-url="teacherImageUrl"
      :size="34"
    />

    <div
      class="chat-bubble mx-2"
      :class="[
        message.role === 'ai' ? 'chat-bubble--ai' : 'chat-bubble--student',
        message.visualElement ? 'chat-bubble--with-visual' : '',
      ]"
    >
      <div v-if="message.role === 'ai' && !isTypewriting" class="reply-text structured-reply text-body-2">
        <template v-for="(block, idx) in replyBlocks" :key="idx">
          <h3 v-if="block.type === 'heading'" class="reply-heading">{{ block.content }}</h3>
          <ol v-else-if="block.type === 'list'" class="reply-list">
            <li v-for="(item, li) in block.items" :key="li" class="reply-list-item">
              <template v-for="(seg, sidx) in buildSegments(item)" :key="`${idx}-li-${li}-${sidx}`">
                <span v-if="seg.type === 'text'" v-html="seg.content" />
                <span
                  v-else
                  class="math-segment"
                  :class="{ 'math-segment--block': seg.display }"
                  v-html="seg.html"
                />
              </template>
            </li>
          </ol>
          <ul v-else-if="block.type === 'bullet_list'" class="reply-bullet-list">
            <li v-for="(item, li) in block.items" :key="li" class="reply-list-item">
              <template v-for="(seg, sidx) in buildSegments(item)" :key="`${idx}-bul-${li}-${sidx}`">
                <span v-if="seg.type === 'text'" v-html="seg.content" />
                <span
                  v-else
                  class="math-segment"
                  :class="{ 'math-segment--block': seg.display }"
                  v-html="seg.html"
                />
              </template>
            </li>
          </ul>
          <p v-else class="reply-paragraph text-body-2 mb-1 lh-relaxed">
            <template v-for="(seg, sidx) in buildSegments(block.content)" :key="`${idx}-p-${sidx}`">
              <span v-if="seg.type === 'text'" v-html="seg.content" />
              <span
                v-else
                class="math-segment"
                :class="{ 'math-segment--block': seg.display }"
                v-html="seg.html"
              />
            </template>
          </p>
        </template>
      </div>
      <p v-else class="text-body-2 mb-1 lh-relaxed reply-text">
        <template v-for="(seg, idx) in displayedSegments" :key="idx">
          <span v-if="seg.type === 'text'" v-html="seg.content" />
          <span
            v-else
            class="math-segment"
            :class="{ 'math-segment--block': seg.display }"
            v-html="seg.html"
          />
        </template>
        <span v-if="isTypewriting" class="typewriter-cursor">▌</span>
      </p>
      <div
        v-if="!isTypewriting && message.role === 'ai' && message.sources?.length"
        class="chat-bubble__sources"
      >
        <button type="button" class="chat-bubble__sources-toggle" @click="showSources = !showSources">
          <v-icon size="12" color="medium-emphasis">mdi-book-open-page-variant</v-icon>
          <span>{{ t('student.chat.sources') }}</span>
          <v-icon size="12" color="medium-emphasis">{{ showSources ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
        </button>
        <div v-if="showSources" class="mt-1">
          <div class="d-flex align-center flex-wrap gap-1 mb-1">
            <v-chip
              v-for="source in message.sources"
              :key="`${source.label}-${source.snippet}`"
              size="x-small"
              color="secondary"
              variant="text"
              class="px-1"
            >
              {{ source.label }}
            </v-chip>
          </div>
          <p class="text-caption source-snippet mb-0">
            {{ message.sources[0].snippet }}
          </p>
        </div>
      </div>
      <audio
        v-if="!isTypewriting && message.audioUrl"
        class="chat-bubble__audio"
        :src="message.audioUrl"
        controls
      />
      <PendulumElement
        v-if="!isTypewriting && message.visualElement?.type === 'pendulum'"
        :caption="message.visualElement.caption"
        :length-m="message.visualElement.length_m"
        @reveal="$emit('reveal')"
      />
      <ConceptDiagramElement
        v-if="!isTypewriting && message.visualElement?.type === 'concept_diagram'"
        :title="message.visualElement.title"
        :layout="message.visualElement.layout"
        :nodes="message.visualElement.nodes"
        @reveal="$emit('reveal')"
      />
      <MathAlgorithmElement
        v-if="!isTypewriting && message.visualElement?.type === 'math_algorithm'"
        :title="message.visualElement.title"
        :algorithm="message.visualElement.algorithm"
        :a="message.visualElement.a"
        :b="message.visualElement.b"
        @reveal="$emit('reveal')"
      />
      <span class="chat-bubble__meta">{{ message.time }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import LessonChatTeacherAvatar from './LessonChatTeacherAvatar.vue'
import PendulumElement from './chat-elements/PendulumElement.vue'
import ConceptDiagramElement from './chat-elements/ConceptDiagramElement.vue'
import MathAlgorithmElement from './chat-elements/MathAlgorithmElement.vue'

const { t } = useI18n()

const props = defineProps({
  message: { type: Object, required: true },
  teacherName: { type: String, default: '' },
  teacherImageUrl: { type: String, default: null },
})

const emit = defineEmits(['reveal'])

const showSources = ref(false)

const MATH_PATTERN = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function formatInlineText(text) {
  return escapeHtml(text).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

function formatBullets(text) {
  return formatInlineText(text).replace(/^[ \t]*[-•]\s+/gm, '• ')
}

function parseReplyBlocks(text) {
  const blocks = []
  const lines = (text || '').split('\n')
  let paragraph = []
  let listItems = []
  let bulletItems = []

  const flushParagraph = () => {
    if (!paragraph.length) return
    blocks.push({ type: 'paragraph', content: paragraph.join('\n') })
    paragraph = []
  }

  const flushList = () => {
    if (!listItems.length) return
    blocks.push({ type: 'list', items: [...listItems] })
    listItems = []
  }

  const flushBulletList = () => {
    if (!bulletItems.length) return
    blocks.push({ type: 'bullet_list', items: [...bulletItems] })
    bulletItems = []
  }

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      flushParagraph()
      flushList()
      flushBulletList()
      continue
    }
    if (trimmed.startsWith('## ')) {
      flushParagraph()
      flushList()
      flushBulletList()
      blocks.push({ type: 'heading', content: trimmed.slice(3).trim() })
      continue
    }
    const numbered = trimmed.match(/^\d+\.\s+(.*)$/)
    if (numbered) {
      flushParagraph()
      flushBulletList()
      listItems.push(numbered[1])
      continue
    }
    const bullet = trimmed.match(/^[-•]\s+(.*)$/)
    if (bullet) {
      flushParagraph()
      flushList()
      bulletItems.push(bullet[1])
      continue
    }
    flushList()
    flushBulletList()
    paragraph.push(line)
  }

  flushParagraph()
  flushList()
  flushBulletList()
  return blocks.length ? blocks : [{ type: 'paragraph', content: text || '' }]
}

function buildSegments(text) {
  const segments = []
  let lastIndex = 0
  let match

  MATH_PATTERN.lastIndex = 0
  while ((match = MATH_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', content: formatBullets(text.slice(lastIndex, match.index)) })
    }
    const display = match[1] !== undefined
    const expression = display ? match[1] : match[2]
    try {
      segments.push({
        type: 'math',
        display,
        html: katex.renderToString(expression.trim(), {
          throwOnError: false,
          displayMode: display,
        }),
      })
    } catch {
      segments.push({ type: 'text', content: match[0] })
    }
    lastIndex = MATH_PATTERN.lastIndex
  }

  if (lastIndex < text.length) {
    segments.push({ type: 'text', content: formatBullets(text.slice(lastIndex)) })
  }

  return segments.length ? segments : [{ type: 'text', content: formatBullets(text) }]
}

const fullSegments = computed(() => buildSegments(props.message.text || ''))
const replyBlocks = computed(() => {
  if (props.message.role !== 'ai') return []
  return parseReplyBlocks(props.message.text || '')
})

const isTypewriting = ref(props.message.role === 'ai' && !!props.message.typewriter)
const revealedSegments = ref(0)
const partialText = ref('')
let timer = null

const displayedSegments = computed(() => {
  if (!isTypewriting.value) return fullSegments.value

  const segs = fullSegments.value
  const result = segs.slice(0, revealedSegments.value)
  if (revealedSegments.value < segs.length && partialText.value) {
    result.push({ type: 'text', content: partialText.value })
  }
  return result
})

function startTypewriter() {
  const segs = fullSegments.value
  timer = setInterval(() => {
    if (revealedSegments.value >= segs.length) {
      clearInterval(timer)
      timer = null
      isTypewriting.value = false
      return
    }
    const current = segs[revealedSegments.value]
    if (current.type !== 'text') {
      revealedSegments.value += 1
      partialText.value = ''
    } else {
      const nextLength = partialText.value.length + 2
      if (nextLength >= current.content.length) {
        partialText.value = ''
        revealedSegments.value += 1
      } else {
        partialText.value = current.content.slice(0, nextLength)
      }
    }
    emit('reveal')
  }, 18)
}

onMounted(() => {
  if (isTypewriting.value) startTypewriter()
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.avatar-student {
  background: linear-gradient(135deg, #3b82f6, #22d3ee) !important;
}

.chat-bubble--with-visual {
  max-width: min(95%, 760px);
}

.lh-relaxed {
  line-height: 1.6;
}

.reply-text {
  word-break: break-word;
}

.structured-reply .reply-paragraph {
  white-space: pre-line;
}

.reply-heading {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--em-primary-deep);
  margin: 0.5rem 0 0.35rem;
  line-height: 1.35;
}

.structured-reply > .reply-heading:first-child {
  margin-top: 0;
}

.reply-paragraph {
  margin: 0 0 0.45rem;
}

.reply-paragraph:last-child {
  margin-bottom: 0;
}

.reply-list,
.reply-bullet-list {
  margin: 0.15rem 0 0.5rem 1rem;
  padding: 0;
}

.reply-list-item {
  margin-bottom: 0.25rem;
  line-height: 1.55;
}

.reply-text :deep(strong) {
  color: var(--em-primary);
  font-weight: 600;
}

.typewriter-cursor {
  display: inline-block;
  margin-inline-start: 2px;
  color: var(--em-cyan);
  animation: cursor-blink 0.9s steps(2, start) infinite;
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  50.01%, 100% { opacity: 0; }
}

.source-snippet {
  color: var(--em-text-muted);
  line-height: 1.5;
  font-size: 0.72rem;
}

.math-segment {
  display: inline-block;
  direction: ltr;
  unicode-bidi: isolate;
  padding: 1px 4px;
  margin: 1px 2px;
  border-radius: 4px;
  background: var(--em-cyan-soft);
  border: 1px solid var(--em-border-bright);
  vertical-align: middle;
}

.math-segment--block {
  display: block;
  margin: 6px 0;
  padding: 8px 10px;
  text-align: center;
  overflow-x: auto;
}
</style>
