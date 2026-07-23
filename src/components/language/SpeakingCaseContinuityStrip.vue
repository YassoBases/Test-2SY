<template>
  <section
    class="spk-case-strip glass-card"
    :class="`spk-case-strip--${mode}`"
    :aria-label="t('student.languages.speakingJourney.liveBridge.continuityCaseLabel')"
  >
    <div class="spk-case-strip__head">
      <div class="spk-case-strip__title-block">
        <span class="spk-case-strip__eyebrow">
          {{ t('student.languages.speakingJourney.liveBridge.continuityCaseLabel') }}
        </span>
        <h4 class="spk-case-strip__title">{{ storyTitle || '—' }}</h4>
      </div>
      <span class="spk-case-strip__mode-badge" :class="`is-${mode}`">
        <v-icon size="14" aria-hidden="true">{{ modeIcon }}</v-icon>
        {{ modeLabel }}
      </span>
    </div>

    <div class="spk-case-strip__chips" role="list">
      <span v-if="studentRole" class="spk-case-strip__chip spk-case-strip__chip--role" role="listitem">
        <v-icon size="13" aria-hidden="true">mdi-account-star-outline</v-icon>
        {{ studentRole }}
      </span>
      <span
        v-for="(character, idx) in visibleCharacters"
        :key="`spk-case-char-${idx}`"
        class="spk-case-strip__chip"
        role="listitem"
      >
        <v-icon size="13" aria-hidden="true">mdi-account-outline</v-icon>
        {{ character }}
      </span>
      <span v-if="extraCharacterCount > 0" class="spk-case-strip__chip spk-case-strip__chip--muted" role="listitem">
        +{{ extraCharacterCount }}
      </span>
      <span v-if="decision" class="spk-case-strip__chip spk-case-strip__chip--decision" role="listitem">
        <v-icon size="13" aria-hidden="true">mdi-source-branch</v-icon>
        {{ decision }}
      </span>
      <span
        v-for="(word, idx) in visibleVocabulary"
        :key="`spk-case-vocab-${idx}`"
        class="spk-case-strip__chip spk-case-strip__chip--vocab"
        role="listitem"
      >
        {{ word }}
      </span>
      <span v-if="grammarLabel" class="spk-case-strip__chip spk-case-strip__chip--grammar" role="listitem">
        <v-icon size="13" aria-hidden="true">mdi-alphabet-latin</v-icon>
        {{ grammarLabel }}
      </span>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  storyTitle: { type: String, default: '' },
  studentRole: { type: String, default: '' },
  characters: { type: Array, default: () => [] },
  decision: { type: String, default: '' },
  vocabulary: { type: Array, default: () => [] },
  /** Single grammar focus — array (first item used) or string. */
  grammar: { type: [Array, String], default: '' },
  /** brief | scene_practice | live */
  mode: { type: String, default: 'brief' },
})

const { t } = useI18n()

const MAX_VISIBLE_CHARACTERS = 3
const MAX_VISIBLE_VOCAB = 5

const visibleCharacters = computed(() =>
  (props.characters || []).filter(Boolean).slice(0, MAX_VISIBLE_CHARACTERS),
)

const extraCharacterCount = computed(() =>
  Math.max(0, (props.characters || []).filter(Boolean).length - MAX_VISIBLE_CHARACTERS),
)

const visibleVocabulary = computed(() => (props.vocabulary || []).filter(Boolean).slice(0, MAX_VISIBLE_VOCAB))

const grammarLabel = computed(() => {
  if (Array.isArray(props.grammar)) return props.grammar.find(Boolean) || ''
  return props.grammar || ''
})

const MODE_ICONS = {
  brief: 'mdi-clipboard-text-outline',
  scene_practice: 'mdi-drama-masks',
  live: 'mdi-broadcast',
}

const MODE_LABEL_KEYS = {
  brief: 'student.languages.speakingJourney.liveBridge.modeBrief',
  scene_practice: 'student.languages.speakingJourney.liveBridge.modeScenePractice',
  live: 'student.languages.speakingJourney.liveBridge.modeLive',
}

const modeIcon = computed(() => MODE_ICONS[props.mode] || MODE_ICONS.brief)
const modeLabel = computed(() => t(MODE_LABEL_KEYS[props.mode] || MODE_LABEL_KEYS.brief))
</script>

<style scoped>
.spk-case-strip {
  position: sticky;
  top: 0.5rem;
  z-index: 5;
  padding: 0.85rem 1.1rem;
  margin-bottom: 1rem;
}

.spk-case-strip__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.spk-case-strip__title-block {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.spk-case-strip__eyebrow {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.6;
}

.spk-case-strip__title {
  font-size: 0.95rem;
  font-weight: 750;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.spk-case-strip__mode-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.spk-case-strip__mode-badge.is-brief {
  background: rgba(var(--v-theme-secondary), 0.14);
  color: rgb(var(--v-theme-secondary));
}

.spk-case-strip__mode-badge.is-scene_practice {
  background: rgba(var(--v-theme-primary), 0.14);
  color: rgb(var(--v-theme-primary));
}

.spk-case-strip__mode-badge.is-live {
  background: rgba(var(--v-theme-success), 0.16);
  color: rgb(var(--v-theme-success));
  animation: spk-case-strip-live-pulse 2.2s ease-in-out infinite;
}

.spk-case-strip__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.spk-case-strip__chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.28rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: rgba(var(--v-theme-on-surface), 0.05);
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.spk-case-strip__chip--role {
  background: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
}

.spk-case-strip__chip--decision {
  background: rgba(var(--v-theme-secondary), 0.12);
  color: rgb(var(--v-theme-secondary));
}

.spk-case-strip__chip--vocab {
  background: rgba(76, 175, 80, 0.12);
  color: #2e7d32;
}

.spk-case-strip__chip--grammar {
  background: rgba(var(--v-theme-info), 0.14);
  color: rgb(var(--v-theme-info));
}

.spk-case-strip__chip--muted {
  opacity: 0.6;
}

@keyframes spk-case-strip-live-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(var(--v-theme-success), 0.35);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(var(--v-theme-success), 0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spk-case-strip__mode-badge.is-live {
    animation: none;
  }
}

@media (max-width: 599px) {
  .spk-case-strip {
    position: static;
  }
  .spk-case-strip__title {
    max-width: 60vw;
  }
}
</style>
