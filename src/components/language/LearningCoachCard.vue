<template>
  <v-card class="glass-card learning-coach pa-5 mb-4" variant="flat">
    <div class="d-flex align-start gap-3">
      <v-avatar color="secondary" variant="tonal" size="44" class="coach-avatar flex-shrink-0">
        <v-icon>mdi-school-outline</v-icon>
      </v-avatar>
      <div class="flex-grow-1 min-width-0">
        <div v-if="eyebrow" class="text-overline text-medium-emphasis">{{ eyebrow }}</div>
        <div v-if="headline" class="text-subtitle-1 font-weight-bold mb-1">{{ headline }}</div>

        <div v-if="showProgress" class="mb-3">
          <v-progress-linear :model-value="progress" color="secondary" height="8" rounded />
        </div>

        <p v-if="summary" class="text-body-2 mb-2">{{ summary }}</p>

        <ul v-if="bullets.length" class="coach-bullets text-body-2 mb-2">
          <li v-for="(item, idx) in bullets" :key="idx">{{ item }}</li>
        </ul>

        <div v-if="checklist.length" class="coach-checklist mb-2">
          <div v-if="checklistTitle" class="text-body-2 font-weight-medium mb-2">{{ checklistTitle }}</div>
          <div
            v-for="(item, idx) in checklist"
            :key="idx"
            class="d-flex align-start gap-2 text-body-2 mb-1"
          >
            <v-icon :color="item.done ? 'success' : 'warning'" size="18" class="mt-1 flex-shrink-0">
              {{ item.done ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
            <span>{{ item.text }}</span>
          </div>
        </div>

        <p v-if="nextStep" class="text-body-2 font-weight-medium coach-next mb-0">
          <v-icon size="18" color="secondary" class="me-1">mdi-arrow-right-circle-outline</v-icon>
          {{ nextStep }}
        </p>
      </div>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  headline: { type: String, default: '' },
  summary: { type: String, default: '' },
  bullets: { type: Array, default: () => [] },
  checklist: { type: Array, default: () => [] },
  checklistTitle: { type: String, default: '' },
  nextStep: { type: String, default: '' },
  progress: { type: Number, default: 0 },
  showProgress: { type: Boolean, default: false },
})
</script>

<style scoped>
.coach-bullets {
  margin: 0;
  padding-inline-start: 1.1rem;
}
.coach-bullets li + li {
  margin-top: 0.25rem;
}
.coach-next {
  color: rgb(var(--v-theme-secondary));
}
.min-width-0 {
  min-width: 0;
}
</style>
