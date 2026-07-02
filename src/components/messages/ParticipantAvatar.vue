<template>
  <div class="participant-avatar" :style="{ width: sizePx, height: sizePx }">
    <TeacherAvatar
      v-if="role === 'teacher'"
      :name="name"
      :image-url="imageUrl"
      :size="size"
    />
    <v-avatar v-else :size="size" :color="avatarColor" class="participant-avatar__fallback">
      <v-img v-if="imageUrl && !imgFailed" :src="resolvedImage" cover @error="imgFailed = true" />
      <v-icon v-else :size="iconSize" color="white">{{ ROLE_ICONS[role] || 'mdi-account' }}</v-icon>
    </v-avatar>
    <span v-if="showRoleBadge" class="participant-avatar__badge" :class="`participant-avatar__badge--${role}`">
      <v-icon size="10">{{ ROLE_ICONS[role] }}</v-icon>
    </span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import { ROLE_ICONS } from '../../utils/messagingUi.js'
import { mediaUrl } from '../../utils/media.js'

const props = defineProps({
  name: { type: String, default: '' },
  role: { type: String, default: 'student' },
  imageUrl: { type: String, default: null },
  size: { type: [Number, String], default: 48 },
  showRoleBadge: { type: Boolean, default: true },
})

const imgFailed = ref(false)

watch(
  () => props.imageUrl,
  () => {
    imgFailed.value = false
  },
)

const sizePx = computed(() => `${Number(props.size) || 48}px`)
const iconSize = computed(() => Math.round(Number(props.size) * 0.45))

const avatarColor = computed(() => {
  const map = { student: 'cyan-darken-2', parent: 'deep-purple-darken-1' }
  return map[props.role] || 'grey-darken-1'
})

const resolvedImage = computed(() => mediaUrl(props.imageUrl))
</script>

<style scoped>
.participant-avatar {
  position: relative;
  flex-shrink: 0;
}
.participant-avatar__fallback {
  border: 2px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}
.participant-avatar__badge {
  position: absolute;
  bottom: -2px;
  left: -2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(15, 20, 35, 0.9);
}
.participant-avatar__badge--teacher {
  background: rgb(var(--v-theme-primary));
}
.participant-avatar__badge--student {
  background: rgb(var(--v-theme-cyan));
}
.participant-avatar__badge--parent {
  background: rgb(var(--v-theme-secondary));
}
</style>
