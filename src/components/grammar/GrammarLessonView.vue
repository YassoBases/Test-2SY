<template>
  <div class="grammar-lesson">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2 mb-4">
      <v-btn variant="text" prepend-icon="mdi-arrow-left" @click="$emit('back')">
        Back to Grammar Home
      </v-btn>
      <div class="d-flex flex-wrap gap-2">
        <v-chip v-if="lesson.grammar_target" size="small" color="secondary" variant="tonal">
          {{ lesson.grammar_target }}
        </v-chip>
        <v-chip v-if="lesson.difficulty" size="small" variant="tonal" class="text-capitalize">
          {{ lesson.difficulty }}
        </v-chip>
        <v-chip v-if="lesson.estimated_minutes != null" size="small" variant="tonal">
          {{ lesson.estimated_minutes }} min
        </v-chip>
      </div>
    </div>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <div class="text-caption text-medium-emphasis mb-1">Teacher Opening</div>
      <p class="text-body-1 font-weight-medium mb-4" dir="ltr">{{ lesson.teacher_opening }}</p>

      <div class="text-caption text-medium-emphasis mb-1">Lesson Goal</div>
      <p class="text-h6 font-weight-bold mb-0" dir="ltr">{{ lesson.lesson_goal }}</p>
      <p v-if="lesson.lesson_title" class="text-body-2 text-medium-emphasis mt-2 mb-0" dir="ltr">
        {{ lesson.lesson_title }}
      </p>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Warm-up</h3>
      <p class="text-body-2 mb-0" dir="ltr">{{ lesson.warmup }}</p>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Main Activity</h3>
      <p class="text-body-2 mb-0" dir="ltr">{{ lesson.main_activity }}</p>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Follow-up Questions</h3>
      <ol class="grammar-list" dir="ltr">
        <li v-for="(q, i) in lesson.follow_up_questions || []" :key="`q-${i}`">{{ q }}</li>
      </ol>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Teacher Hints</h3>
      <ul class="grammar-list" dir="ltr">
        <li v-for="(h, i) in lesson.teacher_hints || []" :key="`h-${i}`">{{ h }}</li>
      </ul>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Common Mistakes</h3>
      <div
        v-for="(m, i) in lesson.common_mistakes || []"
        :key="`m-${i}`"
        class="mistake-row mb-3"
        dir="ltr"
      >
        <div class="text-caption text-error">Incorrect: {{ m.incorrect }}</div>
        <div class="text-caption text-success">Correct: {{ m.correct }}</div>
      </div>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <h3 class="text-subtitle-1 font-weight-bold mb-2">Expected Patterns</h3>
      <div class="d-flex flex-wrap gap-2" dir="ltr">
        <v-chip
          v-for="(p, i) in lesson.expected_patterns || []"
          :key="`p-${i}`"
          size="small"
          variant="outlined"
        >{{ p }}</v-chip>
      </div>
    </v-card>

    <v-card class="glass-card pa-6 mb-4" variant="flat">
      <div class="text-caption text-medium-emphasis mb-1">Completion Message</div>
      <p class="text-body-2 text-medium-emphasis mb-4" dir="ltr">{{ lesson.completion_message }}</p>
      <v-btn color="secondary" variant="flat" size="large" @click="$emit('finish')">
        Finish
      </v-btn>
    </v-card>
  </div>
</template>

<script setup>
defineProps({
  lesson: { type: Object, required: true },
})
defineEmits(['back', 'finish'])
</script>

<style scoped>
.grammar-list {
  margin: 0;
  padding-inline-start: 1.25rem;
  display: grid;
  gap: 0.5rem;
}
.mistake-row {
  padding: 0.5rem 0.75rem;
  border-radius: 0.75rem;
  background: rgba(0, 0, 0, 0.03);
}
</style>
