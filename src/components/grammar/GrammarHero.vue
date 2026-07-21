<template>
  <v-card class="glass-card pa-6 mb-4" variant="flat">
    <div class="text-overline text-medium-emphasis mb-1">Grammar Home</div>
    <h2 class="text-h5 font-weight-bold mb-4">Your Grammar path</h2>

    <div class="grammar-hero__grid">
      <div class="grammar-hero__stat">
        <div class="grammar-hero__label">Current CEFR</div>
        <div class="grammar-hero__value">{{ cefr || '—' }}</div>
      </div>
      <div class="grammar-hero__stat">
        <div class="grammar-hero__label">Current Grammar Topic</div>
        <div class="grammar-hero__value text-body-1">{{ topic || '—' }}</div>
      </div>
      <div class="grammar-hero__stat">
        <div class="grammar-hero__label">Difficulty</div>
        <div class="grammar-hero__value text-body-1 text-capitalize">{{ difficulty || '—' }}</div>
      </div>
      <div class="grammar-hero__stat">
        <div class="grammar-hero__label">Estimated Lesson Time</div>
        <div class="grammar-hero__value">{{ minutes != null ? `${minutes} min` : '—' }}</div>
      </div>
    </div>

    <div v-if="lessonGoal" class="mt-4">
      <div class="text-caption text-medium-emphasis mb-1">Lesson Goal</div>
      <p class="text-body-1 font-weight-medium mb-0" dir="ltr">{{ lessonGoal }}</p>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  cefr: { type: String, default: '' },
  topic: { type: String, default: '' },
  difficulty: { type: String, default: '' },
  minutes: { type: Number, default: null },
  lessonGoal: { type: String, default: '' },
})
</script>

<style scoped>
.grammar-hero__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
@media (min-width: 960px) {
  .grammar-hero__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
.grammar-hero__stat {
  padding: 0.75rem 0.85rem;
  border-radius: 0.85rem;
  background: rgba(var(--neon, 45, 212, 191), 0.08);
  border: 1px solid rgba(var(--neon, 45, 212, 191), 0.16);
}
.grammar-hero__label {
  font-size: 0.72rem;
  letter-spacing: 0.02em;
  color: rgba(var(--v-theme-on-surface), 0.55);
  margin-bottom: 0.25rem;
}
.grammar-hero__value {
  font-weight: 700;
  line-height: 1.3;
}
</style>
