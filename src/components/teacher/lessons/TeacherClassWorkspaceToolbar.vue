<template>
  <div class="class-workspace-toolbar">
    <div class="class-workspace-toolbar__head">
      <div class="class-workspace-toolbar__head-text">
        <h2 class="class-workspace-toolbar__title">{{ displayTitle }}</h2>
        <p v-if="showCount" class="class-workspace-toolbar__count">{{ countLabel }}</p>
      </div>
      <div v-if="$slots.actions" class="class-workspace-toolbar__actions">
        <slot name="actions" />
      </div>
    </div>

    <div
      v-if="showSearch || showFilterShell"
      class="class-workspace-toolbar__controls"
    >
      <div v-if="showSearch" class="class-workspace-toolbar__search-wrap">
        <v-text-field
          :model-value="search"
          density="compact"
          variant="outlined"
          hide-details
          rounded="lg"
          prepend-inner-icon="mdi-magnify"
          :placeholder="$t('teacher.lessons.searchPlaceholder')"
          class="class-workspace-toolbar__search"
          @update:model-value="$emit('update:search', $event)"
        />
      </div>

      <div v-if="showFilterShell" class="class-workspace-toolbar__filters" aria-hidden="true">
        <span class="class-workspace-toolbar__filter-chip class-workspace-toolbar__filter-chip--active">{{ $t('common.all') }}</span>
        <span class="class-workspace-toolbar__filter-chip">{{ $t('teacher.labels.status') }}</span>
        <span class="class-workspace-toolbar__filter-chip">{{ $t('teacher.labels.type') }}</span>
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
  showCount: { type: Boolean, default: false },
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
