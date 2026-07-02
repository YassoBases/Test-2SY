<template>
  <div class="teacher-quiz-toolbar">
    <div class="teacher-quiz-toolbar__row">
      <v-text-field
        :model-value="search"
        :placeholder="$t('teacher.quizzes.searchPlaceholder')"
        variant="outlined"
        density="compact"
        hide-details
        prepend-inner-icon="mdi-magnify"
        class="teacher-quiz-toolbar__search"
        @update:model-value="$emit('update:search', $event)"
      />
      <span class="teacher-quiz-toolbar__sort">{{ $t('teacher.quizzes.sortNewest') }}</span>
    </div>

    <div class="teacher-quiz-toolbar__filters" role="group" :aria-label="$t('teacher.quizzes.filterLabel')">
      <button
        v-for="chip in chips"
        :key="chip.value"
        type="button"
        class="teacher-quiz-toolbar__chip"
        :class="{ 'teacher-quiz-toolbar__chip--active': statusFilter === chip.value }"
        @click="$emit('update:statusFilter', chip.value)"
      >
        {{ chip.label }}
        <span class="teacher-quiz-toolbar__chip-count">{{ chip.count }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  search: { type: String, default: '' },
  statusFilter: { type: String, default: 'all' },
  chips: { type: Array, default: () => [] },
})

defineEmits(['update:search', 'update:statusFilter'])
</script>
