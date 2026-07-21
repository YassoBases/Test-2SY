<template>
  <section
    v-if="blocks.length || support.length"
    class="teaching-blocks mb-5"
    :class="`teaching-blocks--${layout}`"
    :aria-label="t('student.languages.speakingJourney.teaching.title')"
  >
    <div class="d-flex flex-wrap align-center justify-space-between gap-2 mb-3">
      <div class="text-subtitle-1 font-weight-bold mb-0">
        {{ t('student.languages.speakingJourney.teaching.title') }}
      </div>
      <div v-if="layout === 'focus' && blocks.length > 1" class="text-caption text-medium-emphasis">
        {{ focusIndex + 1 }} / {{ blocks.length }}
      </div>
    </div>

    <div v-if="support.length" class="support-row mb-3">
      <v-chip
        v-for="(chip, i) in support"
        :key="`sup-${i}`"
        size="small"
        variant="tonal"
        color="primary"
        class="me-1 mb-1"
      >
        {{ chipLabel(chip) }}
      </v-chip>
    </div>

    <template v-if="layout === 'focus' && blocks.length">
      <article class="teaching-card teaching-card--hero glass-card pa-5 mb-3">
        <div class="d-flex align-start gap-3">
          <div class="icon-wrap" :class="`icon-wrap--${meta(focusBlock.kind).color}`" aria-hidden="true">
            <v-icon :color="meta(focusBlock.kind).color" size="24">{{ meta(focusBlock.kind).icon }}</v-icon>
          </div>
          <div class="min-width-0 flex-grow-1">
            <div class="text-caption text-medium-emphasis mb-1">
              {{ meta(focusBlock.kind).label }}
            </div>
            <div class="text-h6 font-weight-bold mb-2">{{ focusBlock.title }}</div>
            <p class="text-body-1 mb-0" dir="auto">{{ focusBlock.body }}</p>
          </div>
        </div>
      </article>
      <div v-if="blocks.length > 1" class="d-flex gap-2 mb-3">
        <v-btn
          size="small"
          variant="tonal"
          :disabled="focusIndex <= 0"
          prepend-icon="mdi-chevron-left"
          @click="focusIndex -= 1"
        >
          {{ t('student.languages.speakingJourney.teaching.prev') }}
        </v-btn>
        <v-btn
          size="small"
          variant="tonal"
          :disabled="focusIndex >= blocks.length - 1"
          append-icon="mdi-chevron-right"
          @click="focusIndex += 1"
        >
          {{ t('student.languages.speakingJourney.teaching.next') }}
        </v-btn>
      </div>
      <div v-if="groupedSecondary.length" class="grouped-notes">
        <div
          v-for="group in groupedSecondary"
          :key="group.key"
          class="group-block mb-3"
        >
          <div class="text-caption text-medium-emphasis mb-2">{{ group.label }}</div>
          <div class="blocks-grid blocks-grid--compact">
            <article
              v-for="(block, idx) in group.items"
              :key="`${group.key}-${idx}`"
              class="teaching-card glass-card pa-3"
            >
              <div class="text-body-2 font-weight-medium mb-1">{{ block.title }}</div>
              <p class="text-caption mb-0" dir="auto">{{ block.body }}</p>
            </article>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="blocks.length">
      <div
        v-for="group in groupedAll"
        :key="group.key"
        class="group-block mb-4"
      >
        <div class="text-caption text-medium-emphasis mb-2">{{ group.label }}</div>
        <div class="blocks-grid">
          <article
            v-for="(block, idx) in group.items"
            :key="`${group.key}-${idx}`"
            class="teaching-card glass-card pa-4"
            :class="{ 'teaching-card--highlight': isHighlight(block.kind) }"
          >
            <div class="d-flex align-start gap-3">
              <div class="icon-wrap" aria-hidden="true">
                <v-icon :color="meta(block.kind).color" size="22">{{ meta(block.kind).icon }}</v-icon>
              </div>
              <div class="min-width-0 flex-grow-1">
                <div class="text-caption text-medium-emphasis mb-1">
                  {{ meta(block.kind).label }}
                </div>
                <div class="text-body-1 font-weight-medium mb-1">{{ block.title }}</div>
                <p class="text-body-2 mb-0" dir="auto">{{ block.body }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </template>

    <v-card
      v-else
      class="glass-card pa-4 text-center"
      variant="flat"
    >
      <p class="text-body-2 text-medium-emphasis mb-0">
        {{ t('student.languages.speakingJourney.teaching.empty') }}
      </p>
    </v-card>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { teachingKindMeta } from '../../utils/speakingRuntimeMeta.js'

const props = defineProps({
  blocks: { type: Array, default: () => [] },
  support: { type: Array, default: () => [] },
  /** focus = carousel hero; grid = grouped cards; secondary = compact under other stages */
  layout: { type: String, default: 'grid' },
})

const { t } = useI18n()
const focusIndex = ref(0)

watch(
  () => props.blocks,
  () => {
    focusIndex.value = 0
  },
)

function meta(kind) {
  const base = teachingKindMeta(kind)
  const labelKey = {
    explanation: 'explanation',
    example: 'example',
    noticing_cue: 'tip',
    contrast: 'reminder',
    scaffold: 'strategy',
    guided_prompt: 'prompt',
    misconception_correction: 'reminder',
  }[String(kind || '').toLowerCase()]
  return {
    ...base,
    label: t(
      `student.languages.speakingJourney.teaching.kinds.${labelKey || 'general'}`,
    ),
  }
}

function isHighlight(kind) {
  const k = String(kind || '').toLowerCase()
  return k === 'example' || k === 'noticing_cue' || k === 'guided_prompt'
}

function chipLabel(chip) {
  if (typeof chip === 'string') return chip
  return chip?.label || chip?.title || chip?.text || String(chip?.kind || '')
}

function groupKey(kind) {
  return teachingKindMeta(kind).group || 'notes'
}

function groupLabel(key) {
  return t(`student.languages.speakingJourney.teaching.groups.${key}`)
}

function buildGroups(list) {
  const order = ['concepts', 'examples', 'hints', 'notes']
  const buckets = {}
  for (const block of list || []) {
    const key = groupKey(block.kind)
    if (!buckets[key]) buckets[key] = []
    buckets[key].push(block)
  }
  return order
    .filter((key) => buckets[key]?.length)
    .map((key) => ({ key, label: groupLabel(key), items: buckets[key] }))
}

const focusBlock = computed(() => props.blocks[focusIndex.value] || props.blocks[0] || null)
const groupedAll = computed(() => buildGroups(props.blocks))
const groupedSecondary = computed(() => {
  if (!props.blocks.length || props.blocks.length < 2) return []
  const rest = props.blocks.filter((_, i) => i !== focusIndex.value)
  return buildGroups(rest)
})
</script>

<style scoped>
.blocks-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr;
}
.blocks-grid--compact {
  grid-template-columns: 1fr;
}
@media (min-width: 960px) {
  .blocks-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.teaching-card {
  border-radius: var(--em-radius-md, 16px);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  transition: transform 160ms ease, border-color 160ms ease;
}
.teaching-card--highlight {
  border-color: rgba(var(--v-theme-secondary), 0.28);
  background: rgba(var(--v-theme-secondary), 0.04);
}
.teaching-card--hero {
  border-inline-start: 4px solid rgb(var(--v-theme-primary));
}
@media (prefers-reduced-motion: no-preference) {
  .teaching-card:hover {
    transform: translateY(-1px);
    border-color: rgba(var(--v-theme-primary), 0.22);
  }
}
.icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-primary), 0.1);
  flex-shrink: 0;
}
.support-row {
  display: flex;
  flex-wrap: wrap;
}
.min-width-0 {
  min-width: 0;
}
.teaching-blocks--secondary .teaching-card {
  opacity: 0.92;
}
</style>
