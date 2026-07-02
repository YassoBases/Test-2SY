<template>
  <div
    class="teacher-avatar"
    :class="{ 'teacher-avatar--photo': showPhoto }"
    :style="{ width: sizePx, height: sizePx }"
  >
    <img
      v-if="showPhoto"
      :src="resolvedUrl"
      :alt="name"
      class="teacher-avatar__img"
      @error="onError"
    />
    <span v-else class="teacher-avatar__initials">{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { mediaUrl } from '../../utils/media.js'

const props = defineProps({
  name: { type: String, default: '' },
  imageUrl: { type: String, default: null },
  size: { type: [Number, String], default: 52 },
})

const loadFailed = ref(false)

const sizePx = computed(() => {
  const n = Number(props.size) || 52
  return `${n}px`
})

const initials = computed(() => {
  const parts = (props.name || '?').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2)
  return `${parts[0][0] || ''}${parts[parts.length - 1][0] || ''}`
})

const resolvedUrl = computed(() => {
  const url = props.imageUrl
  if (!url || loadFailed.value) return ''
  return mediaUrl(url)
})

const showPhoto = computed(() => Boolean(resolvedUrl.value) && !loadFailed.value)

watch(
  () => props.imageUrl,
  () => {
    loadFailed.value = false
  },
)

function onError() {
  loadFailed.value = true
}
</script>

<style scoped>
.teacher-avatar {
  flex-shrink: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(145deg, rgba(124, 108, 240, 0.35), rgba(34, 211, 238, 0.2));
  border: 2px solid rgba(124, 108, 240, 0.45);
  box-shadow:
    0 0 20px rgba(124, 108, 240, 0.25),
    inset 0 0 12px rgba(255, 255, 255, 0.06);
}

.teacher-avatar--photo {
  border-color: rgba(34, 211, 238, 0.35);
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.2);
}

.teacher-avatar__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-avatar__initials {
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 0 12px rgba(34, 211, 238, 0.4);
}
</style>
