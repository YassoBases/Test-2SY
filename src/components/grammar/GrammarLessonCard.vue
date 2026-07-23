<template>
  <v-card class="glass-card pa-6 mb-4" variant="flat">
    <h3 class="text-subtitle-1 font-weight-bold mb-1">Today's Lesson</h3>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ subtitle }}
    </p>

    <div class="mb-3">
      <div class="text-caption text-medium-emphasis mb-1">Lesson Title</div>
      <div class="text-h6 font-weight-bold" dir="ltr">{{ title || 'Grammar lesson' }}</div>
    </div>

    <div v-if="targets.length" class="mb-3">
      <div class="text-caption text-medium-emphasis mb-2">Grammar Targets</div>
      <div class="d-flex flex-wrap gap-2">
        <v-chip
          v-for="(t, i) in targets"
          :key="`target-${i}`"
          size="small"
          color="secondary"
          variant="tonal"
        >{{ t }}</v-chip>
      </div>
    </div>

    <div class="d-flex flex-wrap gap-2 mb-5">
      <v-chip v-if="minutes != null" size="small" variant="tonal">
        {{ minutes }} min
      </v-chip>
      <v-chip v-if="difficulty" size="small" variant="tonal" class="text-capitalize">
        {{ difficulty }}
      </v-chip>
    </div>

    <v-btn
      color="secondary"
      variant="flat"
      size="large"
      :prepend-icon="hasActiveLesson ? 'mdi-play-circle' : 'mdi-play'"
      :loading="loading"
      :disabled="disabled || loading"
      @click="$emit(hasActiveLesson ? 'continue' : 'start')"
    >
      {{ hasActiveLesson ? 'Continue Lesson' : 'Start Lesson' }}
    </v-btn>
  </v-card>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  targets: { type: Array, default: () => [] },
  minutes: { type: Number, default: null },
  difficulty: { type: String, default: '' },
  hasActiveLesson: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})
defineEmits(['start', 'continue'])
</script>
