<template>
  <div :class="rootClasses">
    <div v-if="icon || $slots.icon" class="tds-empty__icon" aria-hidden="true">
      <slot name="icon">
        <v-icon :icon="icon" :size="iconSize" color="primary" />
      </slot>
    </div>

    <h3 v-if="title" class="tds-empty__title">{{ title }}</h3>
    <p v-if="description || $slots.description" class="tds-empty__desc">
      <slot name="description">{{ description }}</slot>
    </p>

    <div v-if="$slots.actions || actionLabel" class="tds-empty__actions">
      <slot name="actions">
        <TeacherButton
          v-if="actionLabel"
          :variant="actionVariant"
          :to="actionTo"
          :prepend-icon="actionIcon"
          @click="$emit('action')"
        >
          {{ actionLabel }}
        </TeacherButton>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TeacherButton from './TeacherButton.vue'

const props = defineProps({
  icon: { type: String, default: 'mdi-folder-open-outline' },
  iconSize: { type: [Number, String], default: 32 },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionIcon: { type: String, default: 'mdi-plus' },
  actionTo: { type: [String, Object], default: undefined },
  actionVariant: { type: String, default: 'primary' },
  compact: { type: Boolean, default: false },
})

defineEmits(['action'])

const rootClasses = computed(() => [
  'tds-scope',
  'tds-empty',
  props.compact && 'tds-empty--compact',
])
</script>
