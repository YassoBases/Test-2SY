<template>
  <v-card :class="['glass-card', 'word-rich-card', { 'word-rich-card--large': large }, 'h-100']" variant="flat">
    <div class="word-rich-card__media">
      <transition name="word-card-fade">
        <v-img
          v-if="imageUrl"
          :key="imageUrl"
          :src="imageUrl"
          :height="large ? 300 : 150"
          cover
          class="word-rich-card__img"
        />
      </transition>
      <div v-if="!imageUrl" class="word-rich-card__media-placeholder" :style="{ height: large ? '300px' : '150px' }">
        <v-progress-circular v-if="imageLoading" indeterminate :size="large ? 32 : 22" color="secondary" />
        <v-icon v-else :size="large ? 44 : 28" color="secondary" icon="mdi-image-outline" />
      </div>
    </div>

    <div :class="large ? 'pa-7' : 'pa-3'">
      <div class="d-flex align-center justify-space-between gap-2" :class="large ? 'mb-2' : 'mb-1'">
        <span :class="large ? 'text-h4' : 'text-subtitle-1'" class="font-weight-bold" dir="ltr">{{ word.word }}</span>
        <div class="d-flex gap-1">
          <v-chip v-if="word.cefr_level" :size="large ? 'small' : 'x-small'" color="secondary" variant="tonal">{{ word.cefr_level }}</v-chip>
          <v-chip v-if="dueBadge" :size="large ? 'small' : 'x-small'" color="warning" variant="tonal">due</v-chip>
          <v-chip v-if="statusLabel" :size="large ? 'small' : 'x-small'" variant="tonal">{{ statusLabel }}</v-chip>
        </div>
      </div>

      <div
        v-if="word.part_of_speech"
        class="text-medium-emphasis font-italic"
        :class="large ? 'text-body-2 mb-4' : 'text-caption mb-1'"
      >{{ word.part_of_speech }}</div>

      <p v-if="word.example" :class="large ? 'text-h6 font-weight-regular mb-5' : 'text-body-2 mb-2'" dir="ltr" style="line-height: 1.5">
        <em>{{ word.example }}</em>
      </p>

      <div v-if="word.translation_ar || word.example_ar" :class="large ? 'mb-5' : 'mb-2'">
        <v-btn
          :size="large ? 'default' : 'x-small'" variant="tonal" color="secondary"
          :prepend-icon="arabicRevealed ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
          @click="arabicRevealed = !arabicRevealed"
        >
          <template v-if="arabicRevealed">Hide Arabic — اخفاء الترجمة</template>
          <template v-else>Show Arabic — اظهر الترجمة</template>
        </v-btn>
        <template v-if="arabicRevealed">
          <div
            v-if="word.translation_ar" dir="auto" class="font-weight-medium"
            :class="large ? 'text-h6 mt-3 mb-2' : 'text-body-1 mt-2 mb-1'"
          >{{ word.translation_ar }}</div>
          <p
            v-if="word.example_ar" dir="auto" class="text-medium-emphasis mb-0"
            :class="large ? 'text-body-1' : 'text-body-2'" style="line-height: 1.5"
          >{{ word.example_ar }}</p>
        </template>
      </div>

      <WordPronunciation :word="word.word" :large="large" :class="large ? 'mb-5' : 'mb-2'" />

      <div
        v-if="showGrading" class="d-flex flex-wrap justify-center"
        :class="large ? 'gap-2 mt-3' : 'gap-1 mt-1'"
      >
        <v-btn
          :size="large ? 'default' : 'x-small'" :class="{ 'flex-grow-1': large }" color="error" variant="tonal"
          :loading="gradingQuality === 1" :disabled="gradingQuality !== null && gradingQuality !== 1"
          @click="$emit('grade', 1)"
        >Again</v-btn>
        <v-btn
          :size="large ? 'default' : 'x-small'" :class="{ 'flex-grow-1': large }" color="warning" variant="tonal"
          :loading="gradingQuality === 3" :disabled="gradingQuality !== null && gradingQuality !== 3"
          @click="$emit('grade', 3)"
        >Hard</v-btn>
        <v-btn
          :size="large ? 'default' : 'x-small'" :class="{ 'flex-grow-1': large }" color="secondary" variant="tonal"
          :loading="gradingQuality === 4" :disabled="gradingQuality !== null && gradingQuality !== 4"
          @click="$emit('grade', 4)"
        >Good</v-btn>
        <v-btn
          :size="large ? 'default' : 'x-small'" :class="{ 'flex-grow-1': large }" color="success" variant="flat"
          :loading="gradingQuality === 5" :disabled="gradingQuality !== null && gradingQuality !== 5"
          @click="$emit('grade', 5)"
        >Easy</v-btn>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import WordPronunciation from './WordPronunciation.vue'

defineProps({
  word: { type: Object, required: true }, // { word, translation_ar, example, example_ar, part_of_speech, cefr_level }
  imageUrl: { type: String, default: '' },
  imageLoading: { type: Boolean, default: false },
  statusLabel: { type: String, default: '' },
  dueBadge: { type: Boolean, default: false },
  showGrading: { type: Boolean, default: false },
  // The SM-2 quality (1/3/4/5) currently being submitted, or null when idle — lets each button
  // show its own loading/disabled state instead of all four reacting to one shared boolean.
  gradingQuality: { type: Number, default: null },
  // Spacious variant for the daily single-card view (VocabularyGenerator.vue). The Review Bank
  // grid keeps the compact default — a grid of "large" cards would break that layout.
  large: { type: Boolean, default: false },
})

defineEmits(['grade'])

// Arabic stays hidden until the student taps to check their understanding — English content
// (word, example sentence, image) is always visible. Callers key this component by word
// identity so the reveal resets when the displayed word changes (see VocabularyGenerator.vue).
const arabicRevealed = ref(false)
</script>

<style scoped>
.word-rich-card {
  display: flex;
  flex-direction: column;
}
.word-rich-card__media {
  position: relative;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
  background: rgba(var(--v-theme-secondary), 0.08);
}
.word-rich-card__media-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Large variant (daily single-card view) — same visual system, more room to breathe. */
.word-rich-card--large {
  border-radius: var(--em-radius-lg) !important;
  box-shadow: var(--em-shadow-card) !important;
}
.word-rich-card--large .word-rich-card__media {
  border-radius: var(--em-radius-lg) var(--em-radius-lg) 0 0;
}

/* Subtle continuous "Ken Burns" motion on the generated illustration — a reliable,
   zero-dependency stand-in for a real animation/video (see report for why). */
.word-rich-card__img {
  animation: word-card-breathe 9s ease-in-out infinite;
  will-change: transform;
}
@keyframes word-card-breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.07); }
}
.word-card-fade-enter-active {
  transition: opacity 0.5s ease;
}
.word-card-fade-enter-from {
  opacity: 0;
}
@media (prefers-reduced-motion: reduce) {
  .word-rich-card__img { animation: none; }
}
</style>
