<template>
  <section class="level-timeline" aria-label="Journey timeline">
    <header class="level-timeline__intro">
      <h2 class="level-timeline__heading">{{ t('student.englishJourney.timeline.title') }}</h2>
      <p class="level-timeline__sub">{{ t('student.englishJourney.timeline.subtitle') }}</p>
    </header>

    <ol class="level-timeline__path">
      <li
        v-for="level in levels"
        :key="level.cefr"
        class="level-timeline__level"
        :class="[
          `level-timeline__level--${level.status}`,
          { 'level-timeline__level--expanded': isOpen(level) },
        ]"
      >
        <div class="level-timeline__rail" aria-hidden="true">
          <span class="level-timeline__dot">
            <v-icon :icon="levelIcon(level)" size="16" />
          </span>
        </div>

        <div class="level-timeline__panel">
          <button
            type="button"
            class="level-timeline__header"
            :aria-expanded="isOpen(level)"
            @click="toggle(level.cefr)"
          >
            <span class="level-timeline__cefr eng-island" dir="ltr">{{ level.cefr }}</span>
            <span class="level-timeline__status">
              {{ levelLabel(level) }}
            </span>
            <span class="level-timeline__count text-medium-emphasis">
              {{ level.completed_count }}/{{ level.total_count }}
            </span>
            <v-icon
              :icon="isOpen(level) ? 'mdi-chevron-up' : 'mdi-chevron-down'"
              size="20"
              aria-hidden="true"
            />
          </button>

          <div v-if="isOpen(level)" class="level-timeline__stages">
            <p class="level-timeline__stages-label">
              {{ t('student.englishJourney.timeline.stagesInLevel', { cefr: level.cefr }) }}
            </p>
            <div class="level-timeline__stage-grid">
              <StageCard
                v-for="stage in level.stages"
                :key="stage.grammar_id"
                :stage="stage"
                @select="$emit('select-stage', $event)"
              />
            </div>
          </div>
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import StageCard from './StageCard.vue'

const props = defineProps({
  levels: { type: Array, default: () => [] },
})

defineEmits(['select-stage'])
const { t } = useI18n()

const openMap = reactive({})

watch(
  () => props.levels,
  (levels) => {
    for (const lv of levels || []) {
      // Always sync expanded from API for the current level; keep user toggles for others.
      if (lv.expanded) {
        openMap[lv.cefr] = true
      } else if (openMap[lv.cefr] === undefined) {
        openMap[lv.cefr] = false
      }
    }
  },
  { immediate: true, deep: true },
)

function isOpen(level) {
  return !!openMap[level.cefr]
}

function toggle(cefr) {
  openMap[cefr] = !openMap[cefr]
}

function levelIcon(level) {
  if (level.status === 'done') return 'mdi-check'
  if (level.status === 'current') return 'mdi-circle'
  return 'mdi-lock-outline'
}

function levelLabel(level) {
  if (level.status === 'done') return t('student.englishJourney.status.done')
  if (level.status === 'current') return t('student.englishJourney.status.levelCurrent')
  return t('student.englishJourney.status.levelLocked')
}
</script>

<style scoped>
.level-timeline__intro {
  margin-block-end: 16px;
}

.level-timeline__heading {
  margin: 0 0 6px;
  font-size: 1.25rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.level-timeline__sub {
  margin: 0;
  color: var(--text-muted, #3f4f63);
  font-size: 0.875rem;
}

.level-timeline__path {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.level-timeline__level {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 12px;
  position: relative;
}

.level-timeline__rail {
  position: relative;
  display: flex;
  justify-content: center;
  padding-block: 18px;
}

.level-timeline__rail::before {
  content: '';
  position: absolute;
  inset-inline: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  background: color-mix(in srgb, var(--color-primary, #6366f1) 28%, transparent);
}

.level-timeline__level:first-child .level-timeline__rail::before {
  top: 28px;
}

.level-timeline__level:last-child .level-timeline__rail::before {
  bottom: calc(100% - 28px);
}

.level-timeline__dot {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #fff;
  color: var(--color-primary-deep, #4f46e5);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary, #6366f1) 20%, transparent);
}

.level-timeline__level--done .level-timeline__dot {
  background: #10b981;
  color: #fff;
  box-shadow: none;
}

.level-timeline__level--locked .level-timeline__dot {
  color: var(--text-muted, #3f4f63);
  box-shadow: 0 0 0 2px rgba(63, 79, 99, 0.2);
}

.level-timeline__panel {
  margin-block-end: 12px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  overflow: hidden;
}

.level-timeline__header {
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

.level-timeline__cefr {
  font-weight: 800;
  font-size: 1.125rem;
  color: var(--color-primary-deep, #4f46e5);
}

.level-timeline__status {
  font-size: 0.8125rem;
}

.level-timeline__stages {
  padding: 0 16px 16px;
}

.level-timeline__stages-label {
  margin: 0 0 12px;
  font-size: 0.8125rem;
  color: var(--text-muted, #3f4f63);
}

.level-timeline__stage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (max-width: 600px) {
  .level-timeline__stage-grid {
    grid-template-columns: 1fr;
  }
}
</style>
