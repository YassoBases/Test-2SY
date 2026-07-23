<template>
  <AppCard class="session-entry" solid padding="lg">
    <div class="session-entry__head">
      <div>
        <p class="session-entry__eyebrow">
          <v-icon icon="mdi-robot-outline" size="18" aria-hidden="true" />
          {{ t('student.englishJourney.sessionEntry.eyebrow') }}
        </p>
        <h2 class="session-entry__title">
          {{ title || t('student.englishJourney.sessionEntry.title') }}
        </h2>
        <p v-if="subtitle" class="session-entry__subtitle eng-island" dir="ltr">
          {{ subtitle }}
        </p>
      </div>
      <span v-if="minutes" class="session-entry__eta">
        {{ t('student.englishJourney.hero.eta', { minutes }) }}
      </span>
    </div>

    <MissionCard v-if="mission" :mission="mission" class="session-entry__mission" />

    <ol v-if="previewSections.length" class="session-entry__preview">
      <li v-for="(sec, i) in previewSections" :key="`${sec.kind}-${i}`">
        <span class="eng-island" dir="ltr">{{ sec.title || sec.kind }}</span>
      </li>
    </ol>

    <div class="session-entry__actions">
      <AppButton
        variant="primary"
        size="large"
        :loading="loading"
        :disabled="disabled"
        prepend-icon="mdi-play-circle"
        @click="$emit('start')"
      >
        {{ disabled ? t('student.englishJourney.hero.ctaDisabled') : t('student.englishJourney.sessionEntry.cta') }}
      </AppButton>
      <AppButton
        v-if="stageTo"
        variant="ghost"
        :to="stageTo"
      >
        {{ t('student.englishJourney.sessionEntry.viewStage') }}
      </AppButton>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import AppButton from '../ui/AppButton.vue'
import MissionCard from './MissionCard.vue'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  mission: { type: Object, default: null },
  sections: { type: Array, default: () => [] },
  minutes: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  stageTo: { type: [String, Object], default: '' },
})

defineEmits(['start'])
const { t } = useI18n()

const previewSections = computed(() => (props.sections || []).slice(0, 5))
</script>

<style scoped>
.session-entry {
  margin-block-start: 28px;
  border: 1px solid color-mix(in srgb, var(--color-primary, #6366f1) 22%, transparent);
}

.session-entry__head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 16px;
}

.session-entry__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 6px;
  font-size: 0.8125rem;
  color: var(--color-primary-deep, #4f46e5);
  font-weight: 600;
}

.session-entry__title {
  margin: 0 0 6px;
  font-family: var(--font-display, Tajawal, sans-serif);
  font-size: 1.35rem;
}

.session-entry__subtitle {
  margin: 0;
  color: var(--text-muted, #3f4f63);
  font-size: 0.9375rem;
}

.session-entry__eta {
  align-self: flex-start;
  padding: 6px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 12%, transparent);
  font-size: 0.8125rem;
  font-weight: 600;
}

.session-entry__mission {
  margin-block-end: 16px;
}

.session-entry__preview {
  margin: 0 0 20px;
  padding-inline-start: 1.25rem;
  color: var(--text-muted, #3f4f63);
  font-size: 0.875rem;
}

.session-entry__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
