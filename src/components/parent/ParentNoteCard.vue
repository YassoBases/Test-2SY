<template>
  <v-card
    class="parent-note-card"
    variant="flat"
    :class="{ 'parent-note-card--unread': unread }"
  >
    <div class="d-flex align-start justify-space-between gap-3 mb-3">
      <div class="flex-grow-1 min-w-0">
        <h4
          class="parent-note-card__title"
          :class="{ 'parent-note-card__title--placeholder': titleEmpty }"
        >
          {{ displayTitle }}
        </h4>
        <div class="d-flex flex-wrap gap-1 mt-2">
          <v-chip size="x-small" :color="categoryColor" variant="tonal">
            {{ noteCategory(note.category, note.category_label_ar) }}
          </v-chip>
          <slot name="chips" />
        </div>
      </div>
      <slot name="actions" />
    </div>

    <p
      class="parent-note-card__body"
      :class="{
        'parent-note-card__body--placeholder': bodyEmpty,
        'parent-note-card__body--clamped': shouldClamp && !expanded,
      }"
    >
      {{ displayBody }}
    </p>

    <v-btn
      v-if="showExpand"
      variant="text"
      size="x-small"
      color="secondary"
      class="px-0 mt-1"
      @click="expanded = !expanded"
    >
      {{ expanded ? t('parent.notes.showLess') : t('parent.notes.showMore') }}
    </v-btn>

    <div class="parent-note-card__meta text-caption text-medium-emphasis mt-3">
      <slot name="meta">
        {{ note.created_by_name }} · {{ formattedDate }}
      </slot>
    </div>
  </v-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'
import {
  parentNoteBodyIsEmpty,
  parentNoteDisplayBody,
  parentNoteDisplayTitle,
  parentNoteTitleIsEmpty,
} from '../../utils/parentNoteDisplay.js'
import { PARENT_NOTE_CATEGORY_COLORS } from '../../constants/parentNoteCategories.js'

const props = defineProps({
  note: { type: Object, required: true },
  unread: { type: Boolean, default: false },
  formattedDate: { type: String, default: '' },
  clampLines: { type: Number, default: 8 },
  clampBody: { type: Boolean, default: false },
})

const { t } = useI18n()
const { noteCategory } = useLocalizedLabels()

const expanded = ref(false)

const displayTitle = computed(() => parentNoteDisplayTitle(props.note))
const displayBody = computed(() => parentNoteDisplayBody(props.note))
const titleEmpty = computed(() => parentNoteTitleIsEmpty(props.note))
const bodyEmpty = computed(() => parentNoteBodyIsEmpty(props.note))

const categoryColor = computed(
  () => PARENT_NOTE_CATEGORY_COLORS[props.note.category] || 'primary',
)

const shouldClamp = computed(() => {
  if (props.clampBody) return true
  const body = displayBody.value
  return body.length > 280 || body.split('\n').length > props.clampLines
})

const showExpand = computed(() => shouldClamp.value)
</script>

<style scoped>
.parent-note-card {
  background: rgba(18, 26, 50, 0.96) !important;
  border: 1px solid rgba(124, 108, 240, 0.22) !important;
  border-radius: 14px !important;
  padding: 1rem 1.125rem !important;
  color: var(--em-text) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.parent-note-card--unread {
  border-inline-start: 3px solid rgb(var(--v-theme-error)) !important;
  padding-inline-start: calc(1.125rem - 3px) !important;
}

.parent-note-card__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.0625rem;
  font-weight: 700;
  line-height: 1.45;
  color: #f0f3fa !important;
  word-break: break-word;
}

.parent-note-card__title--placeholder {
  color: var(--em-text-muted) !important;
  font-style: italic;
  font-weight: 600;
}

.parent-note-card__body {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.65;
  color: rgba(232, 236, 244, 0.92) !important;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.parent-note-card__body--placeholder {
  color: var(--em-text-muted) !important;
  font-style: italic;
}

.parent-note-card__body--clamped {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 8;
  overflow: hidden;
  white-space: pre-wrap;
}

.parent-note-card__meta {
  opacity: 1;
}
</style>
