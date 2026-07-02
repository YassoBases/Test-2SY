<template>
  <div dir="ltr">
    <p class="reply-text text-body-2 mb-0">
      <span
        v-for="(w, i) in words"
        :key="i"
        class="word"
        :class="{ spoken: i <= activeIdx, current: i === activeIdx && playing }"
      >{{ w }}<span v-if="i < words.length - 1">&nbsp;</span></span>
    </p>

    <audio
      v-if="audioUrl"
      ref="audioEl"
      :src="audioUrl"
      controls
      class="w-100 mt-2"
      :autoplay="autoplay"
      @play="playing = true"
      @pause="playing = false"
      @timeupdate="onTime"
      @ended="onEnded"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  text: { type: String, default: '' },
  audioUrl: { type: String, default: null },
  autoplay: { type: Boolean, default: false },
})

const audioEl = ref(null)
const playing = ref(false)
// No audio -> show the whole reply as already "spoken" (no animation to wait on).
const activeIdx = ref(props.audioUrl ? -1 : 9999)

const words = computed(() => (props.text || '').trim().split(/\s+/).filter(Boolean))

function onTime() {
  const a = audioEl.value
  if (!a || !a.duration || !Number.isFinite(a.duration)) return
  // Even distribution of words across the clip — approximates karaoke without exact timings.
  activeIdx.value = Math.min(words.value.length - 1, Math.floor((a.currentTime / a.duration) * words.value.length))
}

function onEnded() {
  playing.value = false
  activeIdx.value = words.value.length - 1
}
</script>

<style scoped>
.reply-text {
  line-height: 1.7;
}
.word {
  color: rgba(var(--v-theme-on-surface), 0.45);
  transition: color 0.15s ease, text-shadow 0.15s ease;
}
.word.spoken {
  color: rgb(var(--v-theme-on-surface));
}
.word.current {
  color: rgb(var(--v-theme-secondary));
  text-shadow: 0 0 10px rgba(var(--v-theme-secondary), 0.5);
}
</style>
