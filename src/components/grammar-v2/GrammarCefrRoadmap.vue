<template>
  <section class="roadmap" aria-label="Grammar CEFR roadmap">
    <header class="roadmap__intro">
      <h2 class="roadmap__heading">{{ t('student.grammarV2.roadmap.title') }}</h2>
      <p class="roadmap__sub">{{ t('student.grammarV2.roadmap.subtitle') }}</p>
    </header>

    <ol class="roadmap__list">
      <li
        v-for="level in levels"
        :key="level.cefr"
        class="roadmap__level"
        :class="[`roadmap__level--${level.status}`, { 'roadmap__level--open': isOpen(level) }]"
      >
        <button
          type="button"
          class="roadmap__header"
          :aria-expanded="isOpen(level)"
          @click="toggle(level.cefr)"
        >
          <span class="roadmap__cefr eng-island" dir="ltr">{{ level.cefr }}</span>
          <span class="roadmap__summary">
            {{
              t('student.grammarV2.roadmap.completedOf', {
                done: level.completed_count,
                total: level.total_count,
              })
            }}
          </span>
          <span class="roadmap__level-status">
            <v-icon :icon="levelIcon(level)" size="16" aria-hidden="true" />
            {{ levelLabel(level) }}
          </span>
          <v-icon
            :icon="isOpen(level) ? 'mdi-chevron-up' : 'mdi-chevron-down'"
            size="20"
            aria-hidden="true"
          />
        </button>

        <div v-if="isOpen(level)" class="roadmap__stages">
          <GrammarStageCard
            v-for="stage in level.stages"
            :key="stage.grammar_id"
            :stage="stage"
            @select="$emit('select-stage', $event)"
          />
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import GrammarStageCard from './GrammarStageCard.vue'

const props = defineProps({
  levels: { type: Array, default: () => [] },
  /** Backend journey.anchor_cefr / progress.cefr_label — never computed client-side. */
  anchorCefr: { type: String, default: '' },
})

defineEmits(['select-stage'])
const { t } = useI18n()
const openMap = reactive({})

/**
 * Sync accordion from journey payload only.
 * Prefer anchor_cefr; fall back to levels[].expanded.
 * Overwrite on every payload fingerprint change so first load opens the current CEFR
 * (not a sticky A1 from a previous sync).
 */
watch(
  () => ({
    fingerprint: (props.levels || [])
      .map((lv) => `${lv.cefr}:${lv.expanded ? 1 : 0}:${lv.status}`)
      .join('|'),
    anchor: props.anchorCefr || '',
  }),
  () => {
    const levels = props.levels || []
    if (!levels.length) return

    const fromExpanded = levels.find((lv) => lv.expanded)?.cefr || ''
    const target = props.anchorCefr || fromExpanded || ''

    for (const key of Object.keys(openMap)) {
      delete openMap[key]
    }
    for (const lv of levels) {
      openMap[lv.cefr] = !!target && lv.cefr === target
    }
  },
  { immediate: true },
)

function isOpen(level) {
  return !!openMap[level.cefr]
}

function toggle(cefr) {
  // Previous levels stay reviewable via toggle; lock status is stage-level only.
  openMap[cefr] = !openMap[cefr]
}

function levelIcon(level) {
  if (level.status === 'done') return 'mdi-check-decagram'
  if (level.status === 'current') return 'mdi-circle'
  return 'mdi-lock-outline'
}

function levelLabel(level) {
  if (level.status === 'done') return t('student.grammarV2.status.levelDone')
  if (level.status === 'current') return t('student.grammarV2.status.levelCurrent')
  return t('student.grammarV2.status.levelLocked')
}
</script>

<style scoped>
.roadmap__intro {
  margin-block-end: 16px;
}

.roadmap__heading {
  margin: 0 0 6px;
  font-size: 1.25rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.roadmap__sub {
  margin: 0;
  color: var(--text-muted, #3f4f63);
  font-size: 0.875rem;
}

.roadmap__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.roadmap__level {
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  overflow: hidden;
}

.roadmap__header {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 16px;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  text-align: start;
}

.roadmap__cefr {
  font-weight: 800;
  font-size: 1.125rem;
  color: var(--color-primary-deep, #4f46e5);
}

.roadmap__summary,
.roadmap__level-status {
  font-size: 0.8125rem;
}

.roadmap__level-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.roadmap__stages {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  padding: 0 16px 16px;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (max-width: 600px) {
  .roadmap__stages {
    grid-template-columns: 1fr;
  }

  .roadmap__header {
    grid-template-columns: auto 1fr auto;
  }

  .roadmap__summary {
    grid-column: 1 / -1;
  }
}
</style>
