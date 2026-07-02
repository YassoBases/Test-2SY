<template>
  <AppCard
    class="app-empty-state empty-state"
    :class="{ 'empty-state--compact': compact }"
    solid
    :padding="compact ? 'sm' : 'lg'"
  >
    <div class="app-empty-state__inner text-center">
      <div class="app-empty-state__icon mx-auto mb-5">
        <v-icon :icon="resolvedIcon" :size="iconSize" :color="iconColor" />
      </div>
      <h3 class="app-empty-state__title">{{ resolvedTitle }}</h3>
      <p class="app-empty-state__desc text-medium-emphasis mb-6 mx-auto">
        {{ resolvedDescription }}
      </p>
      <slot name="action">
        <AppButton
          v-if="resolvedActionLabel"
          variant="primary"
          :to="resolvedActionTo"
          :prepend-icon="resolvedActionIcon"
          @click="$emit('action')"
        >
          {{ resolvedActionLabel }}
        </AppButton>
      </slot>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { emptyStatePreset } from '../../constants/emptyStatePresets.js'
import AppCard from './AppCard.vue'
import AppButton from './AppButton.vue'

const props = defineProps({
  preset: { type: String, default: '' },
  icon: { type: String, default: '' },
  iconSize: { type: [Number, String], default: 48 },
  iconColor: { type: String, default: 'primary' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionTo: { type: String, default: '' },
  actionIcon: { type: String, default: 'mdi-plus' },
  compact: { type: Boolean, default: false },
})

defineEmits(['action'])

const { t } = useI18n()

function resolvePresetText(value, key) {
  if (value) return value
  if (key) return t(key)
  return ''
}

const presetData = computed(() => (props.preset ? emptyStatePreset(props.preset) : null))

const resolvedIcon = computed(() => props.icon || presetData.value?.icon || 'mdi-folder-open-outline')
const resolvedTitle = computed(() =>
  resolvePresetText(props.title, presetData.value?.titleKey),
)
const resolvedDescription = computed(() =>
  resolvePresetText(props.description, presetData.value?.descriptionKey),
)
const resolvedActionLabel = computed(() =>
  resolvePresetText(props.actionLabel, presetData.value?.actionLabelKey),
)
const resolvedActionTo = computed(() => props.actionTo || presetData.value?.actionTo || '')
const resolvedActionIcon = computed(
  () => props.actionIcon || presetData.value?.actionIcon || 'mdi-plus',
)
</script>

<style scoped>
.app-empty-state__icon {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--em-surface-control);
  border: 1px solid var(--em-border-subtle);
}

.empty-state--compact .app-empty-state__icon {
  width: 72px;
  height: 72px;
}

.app-empty-state__title {
  font-family: var(--font-display);
  font-size: var(--em-text-title);
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--em-text);
}

.app-empty-state__desc {
  font-size: var(--em-text-sm);
  max-width: 360px;
  line-height: 1.55;
}
</style>
