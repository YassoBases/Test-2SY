<template>
  <div class="lesson-workspace-toolbar">
    <div class="lesson-workspace-toolbar__titles">
      <h2 class="lesson-workspace-toolbar__title">{{ displayTitle }}</h2>
      <p class="lesson-workspace-toolbar__count">{{ countLabel }}</p>
    </div>

    <div class="lesson-workspace-toolbar__tools">
      <v-text-field
        v-if="showSearch"
        :model-value="search"
        density="compact"
        variant="outlined"
        hide-details
        rounded="lg"
        prepend-inner-icon="mdi-magnify"
        :placeholder="$t('teacher.lessons.searchPlaceholder')"
        class="lesson-workspace-toolbar__search"
        @update:model-value="$emit('update:search', $event)"
      />

      <div v-if="showFilterShell" class="lesson-workspace-toolbar__filters" aria-hidden="true">
        <span class="lesson-workspace-toolbar__filter-chip lesson-workspace-toolbar__filter-chip--active">{{ $t('common.all') }}</span>
        <span class="lesson-workspace-toolbar__filter-chip">{{ $t('teacher.labels.status') }}</span>
        <span class="lesson-workspace-toolbar__filter-chip">{{ $t('teacher.labels.type') }}</span>
      </div>

      <div v-if="$slots.actions" class="lesson-workspace-toolbar__actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


const props = defineProps({
  title: { type: String, default: '' },
  count: { type: Number, default: 0 },
  search: { type: String, default: '' },
  showSearch: { type: Boolean, default: true },
  showFilterShell: { type: Boolean, default: true },
})

defineEmits(['update:search'])

const displayTitle = computed(() => props.title || t('teacher.lessons.defaultToolbarTitle'))

const countLabel = computed(() => {
  const n = props.count
  if (n === 0) return t('teacher.lessons.noLessons')
  if (n === 1) return t('teacher.lessons.oneLessonCount')
  if (n === 2) return t('teacher.lessons.twoLessons')
  return t('teacher.labels.lessonCount', { count: n })
})
</script>
