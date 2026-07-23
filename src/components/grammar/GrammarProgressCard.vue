<template>
  <v-card class="glass-card pa-6 mb-4" variant="flat">
    <h3 class="text-subtitle-1 font-weight-bold mb-4">Current Progress</h3>

    <div class="grammar-progress__grid">
      <div class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Current CEFR</div>
        <div class="text-h6 font-weight-bold">{{ cefr || '—' }}</div>
      </div>
      <div class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Current Grammar Topic</div>
        <div class="text-body-1 font-weight-bold">{{ topic || '—' }}</div>
      </div>
      <div v-if="masteryPercent != null" class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Grammar Mastery %</div>
        <div class="text-h6 font-weight-bold">{{ masteryPercent }}%</div>
      </div>
      <div v-if="completedTopics != null" class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Completed Topics</div>
        <div class="text-h6 font-weight-bold">{{ completedTopics }}</div>
      </div>
      <div v-if="remainingTopics != null" class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Remaining Topics</div>
        <div class="text-h6 font-weight-bold">{{ remainingTopics }}</div>
      </div>
      <div v-if="difficulty" class="grammar-progress__item">
        <div class="text-caption text-medium-emphasis">Difficulty</div>
        <div class="text-body-1 font-weight-bold text-capitalize">{{ difficulty }}</div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
/**
 * Renders only fields supplied by the Grammar dashboard API.
 * Optional mastery / topic counts appear only when the backend sends them —
 * never calculated on the client.
 */
defineProps({
  cefr: { type: String, default: '' },
  topic: { type: String, default: '' },
  difficulty: { type: String, default: '' },
  masteryPercent: { type: [Number, String], default: null },
  completedTopics: { type: [Number, String], default: null },
  remainingTopics: { type: [Number, String], default: null },
})
</script>

<style scoped>
.grammar-progress__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
@media (min-width: 960px) {
  .grammar-progress__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.grammar-progress__item {
  min-width: 0;
}
</style>
