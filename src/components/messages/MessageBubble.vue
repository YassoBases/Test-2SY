<template>
  <div
    class="msg-row"
    :class="alignClass"
    :style="{ animationDelay: `${animationDelay}ms` }"
  >
    <ParticipantAvatar
      v-if="showAvatar"
      class="msg-row__avatar"
      :name="senderName"
      :role="senderRole"
      :image-url="senderAvatarUrl"
      :size="32"
      :show-role-badge="false"
    />

    <div class="msg-bubble-wrap">
      <div
        class="msg-bubble"
        :class="{ 'msg-bubble--media': isMediaBubble, 'msg-bubble--hoverable': !msg.is_deleted }"
      >
        <div
          v-if="showSenderHeader"
          class="msg-sender-name"
          :class="`msg-sender-name--${senderRole}`"
        >
          {{ msg.sender_name }}
        </div>

        <template v-if="msg.is_deleted">
          <p class="msg-body msg-body--deleted">{{ t('messages.bubble.messageDeleted') }}</p>
        </template>

        <template v-else-if="msg.message_kind === 'image' && msg.attachment_url">
          <img
            :src="mediaUrl(msg.attachment_url)"
            class="msg-image"
            :alt="msg.attachment_name || t('messages.bubble.imageAlt')"
            loading="lazy"
            @click="openPreview('image', msg)"
          />
          <p v-if="captionText" class="msg-body">{{ captionText }}</p>
        </template>

        <template v-else-if="msg.message_kind === 'voice' && msg.attachment_url">
          <VoiceMessagePlayer
          :key="`voice-${msg.id}-${msg.attachment_url}`"
          :src="msg.attachment_url"
          :duration-ms="msg.voice_duration_ms"
          :mime-type="msg.attachment_mime"
        />
        </template>

        <template v-else-if="msg.attachment_url">
          <div class="msg-attach-row">
            <div class="msg-attach-row__icon">
              <v-icon :color="msg.message_kind === 'pdf' ? 'error' : 'primary'" size="24">
                {{ fileIcon }}
              </v-icon>
            </div>
            <div class="msg-attach-row__info">
              <div class="msg-attach-row__name">{{ msg.attachment_name || t('messages.bubble.attachment') }}</div>
              <div class="msg-attach-row__type">{{ kindLabel }}</div>
            </div>
            <div class="msg-attach-row__actions">
              <v-btn icon size="x-small" variant="text" @click="openPreview('file', msg)">
                <v-icon size="18">mdi-eye-outline</v-icon>
              </v-btn>
              <v-btn
                icon
                size="x-small"
                variant="text"
                :href="mediaUrl(msg.attachment_url)"
                :download="msg.attachment_name || 'download'"
              >
                <v-icon size="18">mdi-download</v-icon>
              </v-btn>
            </div>
          </div>
          <p v-if="captionText" class="msg-body mt-1">{{ captionText }}</p>
        </template>

        <template v-else>
          <p class="msg-body">{{ msg.body }}</p>
        </template>

        <div class="msg-meta">
          <span>{{ formatMessageTime(msg.created_at) }}</span>
          <template v-if="isMine && !msg.is_deleted">
            <span class="msg-status" :class="{ 'msg-meta--read': msg.status === 'read' }">
              <v-icon size="14">{{ statusMeta(msg.status).icon }}</v-icon>
            </span>
            <v-btn
              icon
              size="x-small"
              variant="text"
              class="msg-delete-btn"
              :title="t('messages.bubble.delete')"
              @click="$emit('delete', msg.id)"
            >
              <v-icon size="14">mdi-delete-outline</v-icon>
            </v-btn>
          </template>
        </div>
      </div>
    </div>

    <v-dialog v-model="previewOpen" max-width="960" content-class="wa-lightbox" scrim="black">
      <v-card color="transparent" flat>
        <v-toolbar density="compact" color="transparent">
          <v-toolbar-title class="text-subtitle-2">{{ previewTitle }}</v-toolbar-title>
          <v-spacer />
          <v-btn icon variant="text" @click="previewOpen = false"><v-icon>mdi-close</v-icon></v-btn>
        </v-toolbar>
        <v-card-text class="pa-2">
          <img v-if="previewMode === 'image'" :src="previewSrc" class="wa-lightbox__img" alt="" />
          <iframe v-else-if="previewMode === 'pdf'" :src="previewSrc" class="wa-lightbox__pdf" :title="t('messages.bubble.document')" />
          <p v-else class="text-center py-6 text-medium-emphasis">{{ t('messages.bubble.useDownloadPreview') }}</p>
        </v-card-text>
        <v-card-actions class="px-4 pb-3">
          <v-btn variant="text" size="small" :href="previewSrc" target="_blank" rel="noopener">{{ t('messages.bubble.open') }}</v-btn>
          <v-spacer />
          <v-btn variant="tonal" size="small" prepend-icon="mdi-download" :href="previewSrc" :download="previewDownloadName">
            {{ t('messages.bubble.download') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ParticipantAvatar from './ParticipantAvatar.vue'
import VoiceMessagePlayer from './VoiceMessagePlayer.vue'
import { mediaUrl } from '../../utils/media.js'
import { formatMessageTime, messageAlignClass, resolveIsMine, statusMeta } from '../../utils/messagingUi.js'
import { participantAvatarUrl } from '../../utils/teacherAvatar.js'

const props = defineProps({
  msg: { type: Object, required: true },
  viewerId: { type: Number, default: null },
  participants: { type: Array, default: () => [] },
  isGroup: { type: Boolean, default: false },
  teacherAvatarUrl: { type: String, default: null },
  animationDelay: { type: Number, default: 0 },
})

defineEmits(['delete'])

const { t } = useI18n()

const previewOpen = ref(false)
const previewMode = ref('image')
const previewSrc = ref('')
const previewTitle = ref('')
const previewDownloadName = ref('file')

const senderParticipant = computed(() =>
  (props.participants || []).find((p) => p.user_id === props.msg.sender_id),
)

const senderRole = computed(() => senderParticipant.value?.role || 'student')
const senderName = computed(() => senderParticipant.value?.display_name || props.msg.sender_name)

const senderAvatarUrl = computed(() => {
  const fromParticipant = participantAvatarUrl(
    senderParticipant.value,
    props.teacherAvatarUrl,
    props.viewerId,
  )
  if (fromParticipant) return fromParticipant
  if (senderRole.value === 'teacher') {
    return props.msg.sender_avatar_url || null
  }
  return null
})

const isMine = computed(() => resolveIsMine(props.msg, props.viewerId))

const alignClass = computed(() => messageAlignClass(isMine.value))
const showSenderHeader = computed(() => props.isGroup && !isMine.value)
const showAvatar = computed(() => !isMine.value)

const isMediaBubble = computed(
  () =>
    !props.msg.is_deleted &&
    (props.msg.message_kind === 'image' ||
      props.msg.message_kind === 'voice' ||
      !!props.msg.attachment_url),
)

const captionText = computed(() => {
  const b = props.msg.body || ''
  if (!b || /^[📷📄📎🎤]/.test(b)) return ''
  return b
})

const kindLabel = computed(() => {
  const k = props.msg.message_kind
  if (k === 'pdf') return 'PDF'
  if (k === 'document') return t('messages.bubble.document')
  return t('messages.bubble.file')
})

const fileIcon = computed(() =>
  props.msg.message_kind === 'pdf' ? 'mdi-file-pdf-box' : 'mdi-file-document-outline',
)

function openPreview(mode, msg) {
  previewSrc.value = mediaUrl(msg.attachment_url)
  previewTitle.value = msg.attachment_name || t('messages.bubble.preview')
  previewDownloadName.value = msg.attachment_name || 'download'
  if (mode === 'image' || msg.message_kind === 'image') previewMode.value = 'image'
  else if (msg.message_kind === 'pdf' || (msg.attachment_mime || '').includes('pdf')) previewMode.value = 'pdf'
  else previewMode.value = 'other'
  previewOpen.value = true
}
</script>

<style scoped>
.msg-delete-btn {
  opacity: 0;
  transition: opacity 0.15s;
  margin-inline-start: 2px;
}
.msg-bubble--hoverable:hover .msg-delete-btn {
  opacity: 0.75;
}
.msg-status {
  display: inline-flex;
  line-height: 1;
}
</style>
