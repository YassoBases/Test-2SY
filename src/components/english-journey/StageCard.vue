<template>
  <AppCard
    class="stage-card"
    :class="[`stage-card--${stage.status}`, { 'stage-card--interactive': interactive }]"
    solid
    padding="md"
    :interactive="interactive"
    :tabindex="interactive ? 0 : -1"
    :role="interactive ? 'button' : undefined"
    :aria-disabled="interactive ? undefined : true"
    @click="onActivate"
    @keydown.enter.prevent="onActivate"
    @keydown.space.prevent="onActivate"
  >
    <div class="stage-card__row">
      <span class="stage-card__icon" :aria-hidden="true">
        <v-icon :icon="statusIcon" size="22" />
      </span>
      <div class="stage-card__body">
        <div class="stage-card__head">
          <span v-if="stage.display_code" class="stage-card__code eng-island" dir="ltr">
            {{ stage.display_code }}
          </span>
          <span class="stage-card__status">
            <v-icon :icon="statusIcon" size="14" aria-hidden="true" />
            {{ statusLabel }}
          </span>
        </div>
        <h3 class="stage-card__title eng-island" dir="ltr">{{ stage.display_name }}</h3>
        <p class="stage-card__meta text-medium-emphasis">
          {{ t('student.englishJourney.stage.minutes', { n: stage.estimated_minutes || 18 }) }}
        </p>
      </div>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppCard from '../ui/AppCard.vue'

const props = defineProps({
  stage: { type: Object, required: true },
})

const emit = defineEmits(['select'])
const { t } = useI18n()

const interactive = computed(
  () => props.stage.status === 'current' || props.stage.status === 'completed' || props.stage.status === 'unlocked',
)

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

const statusLabel = computed(() => t(`student.englishJourney.status.${props.stage.status}`))

function onActivate() {
  if (!interactive.value) return
  emit('select', props.stage)
}
</script>

<style scoped>
.stage-card {
  border-radius: 16px !important;
  transition: transform 220ms ease-out, box-shadow 220ms ease-out;
}

.stage-card--interactive {
  cursor: pointer;
}

.stage-card--interactive:hover {
  transform: translateY(-2px);
}

.stage-card--locked {
  opacity: 0.72;
}

.stage-card__row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.stage-card__icon {
  color: var(--color-primary, #6366f1);
}

.stage-card--completed .stage-card__icon {
  color: #10b981;
}

.stage-card--locked .stage-card__icon {
  color: var(--text-muted, #3f4f63);
}

.stage-card__head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-block-end: 4px;
}

.stage-card__code {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary-deep, #4f46e5);
}

.stage-card__status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--text-muted, #3f4f63);
}

.stage-card__title {
  margin: 0 0 4px;
  font-size: 1rem;
  font-weight: 600;
}

.stage-card__meta {
  margin: 0;
  font-size: 0.8125rem;
}

.eng-island {
  unicode-bidi: isolate;
}

@media (prefers-reduced-motion: reduce) {
  .stage-card {
    transition: none;
  }
  .stage-card--interactive:hover {
    transform: none;
  }
}
</style>
