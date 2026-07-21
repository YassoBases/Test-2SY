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
    <div class="stage-card__top">
      <span v-if="stage.display_code" class="stage-card__code eng-island" dir="ltr">
        {{ stage.display_code }}
      </span>
      <span class="stage-card__status">
        <v-icon :icon="statusIcon" size="16" aria-hidden="true" />
        {{ statusLabel }}
      </span>
    </div>
    <h3 class="stage-card__title eng-island" dir="ltr">{{ stage.display_name }}</h3>
    <p class="stage-card__meta">
      {{ t('student.grammarV2.common.minutes', { n: stage.estimated_minutes || 18 }) }}
      · {{ t('student.grammarV2.card.mastery', { n: Math.round(stage.overall_mastery || 0) }) }}
    </p>
    <ul v-if="stage.skills?.length" class="stage-card__skills">
      <li v-for="skill in stage.skills" :key="skill" class="eng-island" dir="ltr">{{ skill }}</li>
    </ul>
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
  () => props.stage.status === 'current' || props.stage.status === 'completed',
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

const statusLabel = computed(() => t(`student.grammarV2.status.${props.stage.status}`))

function onActivate() {
  if (!interactive.value) return
  emit('select', props.stage)
}
</script>

<style scoped>
.stage-card {
  border-radius: 16px !important;
  border: 1px solid transparent;
  transition: transform 220ms ease-out;
}

.stage-card--interactive {
  cursor: pointer;
}

.stage-card--interactive:hover {
  transform: translateY(-2px);
}

.stage-card--completed {
  background: color-mix(in srgb, #10b981 12%, #fff) !important;
  border-color: color-mix(in srgb, #10b981 35%, transparent);
}

.stage-card--current {
  background: color-mix(in srgb, #3b82f6 12%, #fff) !important;
  border-color: color-mix(in srgb, #3b82f6 40%, transparent);
}

.stage-card--unlocked {
  background: #fff !important;
  border-color: rgba(12, 25, 41, 0.08);
}

.stage-card--locked {
  background: #f1f5f9 !important;
  color: #64748b;
  opacity: 0.9;
}

.stage-card__top {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  margin-block-end: 8px;
}

.stage-card__code {
  font-size: 0.75rem;
  font-weight: 800;
}

.stage-card__status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.stage-card__title {
  margin: 0 0 6px;
  font-size: 1.05rem;
}

.stage-card__meta {
  margin: 0 0 10px;
  font-size: 0.8125rem;
  color: var(--text-muted, #3f4f63);
}

.stage-card__skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.stage-card__skills li {
  padding: 4px 8px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.1);
  font-size: 0.75rem;
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
