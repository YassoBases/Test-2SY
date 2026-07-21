<template>
  <AppCard class="stage-detail" solid padding="lg">
    <header class="stage-detail__header">
      <p v-if="stage.display_code" class="stage-detail__code eng-island" dir="ltr">
        {{ stage.display_code }}
      </p>
      <h2 class="stage-detail__title eng-island" dir="ltr">{{ stage.display_name }}</h2>
      <p class="stage-detail__status">
        <v-icon :icon="statusIcon" size="18" aria-hidden="true" />
        {{ t(`student.englishJourney.status.${stage.status}`) }}
      </p>
    </header>

    <dl class="stage-detail__stats">
      <div>
        <dt>{{ t('student.englishJourney.stage.duration') }}</dt>
        <dd>{{ t('student.englishJourney.stage.minutes', { n: stage.estimated_minutes || 18 }) }}</dd>
      </div>
      <div>
        <dt>{{ t('student.englishJourney.stage.mastery') }}</dt>
        <dd>{{ Math.round(stage.overall_mastery || 0) }}%</dd>
      </div>
    </dl>

    <div v-if="stage.skills?.length" class="stage-detail__skills">
      <h3>{{ t('student.englishJourney.stage.skills') }}</h3>
      <ul>
        <li v-for="skill in stage.skills" :key="skill" class="eng-island" dir="ltr">{{ skill }}</li>
      </ul>
    </div>

    <div v-if="sections.length" class="stage-detail__sections">
      <h3>{{ t('student.englishJourney.stage.structure') }}</h3>
      <ol>
        <li v-for="(sec, i) in sections" :key="`${sec.kind}-${i}`">
          <span class="eng-island" dir="ltr">{{ sec.title || sec.kind }}</span>
          <span v-if="sec.estimated_minutes" class="text-medium-emphasis">
            · {{ sec.estimated_minutes }}′
          </span>
        </li>
      </ol>
    </div>

    <p v-if="stage.status === 'locked'" class="stage-detail__hint text-medium-emphasis">
      {{ t('student.englishJourney.stage.lockedHint') }}
    </p>

    <div class="stage-detail__actions">
      <AppButton
        v-if="canStart"
        variant="primary"
        :loading="starting"
        prepend-icon="mdi-play"
        @click="$emit('start')"
      >
        {{ t('student.englishJourney.stage.startSession') }}
      </AppButton>
      <AppButton
        v-else-if="stage.status === 'completed'"
        variant="secondary"
        prepend-icon="mdi-book-refresh"
        @click="$emit('review')"
      >
        {{ t('student.englishJourney.stage.reviewStage') }}
      </AppButton>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'
import AppButton from '../ui/AppButton.vue'

const props = defineProps({
  stage: { type: Object, required: true },
  sections: { type: Array, default: () => [] },
  canStart: { type: Boolean, default: false },
  starting: { type: Boolean, default: false },
})

defineEmits(['start', 'review'])
const { t } = useI18n()

const statusIcon = computed(() => {
  switch (props.stage.status) {
    case 'completed':
      return 'mdi-check-circle'
    case 'current':
      return 'mdi-play-circle'
    case 'unlocked':
      return 'mdi-lock-open-variant-outline'
    default:
      return 'mdi-lock-outline'
  }
})
</script>

<style scoped>
.stage-detail__code {
  margin: 0 0 4px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary, #6366f1);
}

.stage-detail__title {
  margin: 0 0 8px;
  font-size: 1.5rem;
}

.stage-detail__status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 20px;
  font-size: 0.875rem;
}

.stage-detail__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0 0 20px;
}

.stage-detail__stats dt {
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.stage-detail__stats dd {
  margin: 4px 0 0;
  font-weight: 700;
  font-size: 1.25rem;
}

.stage-detail__skills h3,
.stage-detail__sections h3 {
  margin: 0 0 8px;
  font-size: 0.9375rem;
}

.stage-detail__skills ul {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}

.stage-detail__skills li {
  padding: 6px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 10%, transparent);
  font-size: 0.8125rem;
}

.stage-detail__sections ol {
  margin: 0 0 20px;
  padding-inline-start: 1.25rem;
}

.stage-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
