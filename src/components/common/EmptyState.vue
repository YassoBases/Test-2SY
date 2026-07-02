<template>
  <AppEmptyState
    :preset="preset"
    :icon="icon"
    :icon-size="iconSize"
    :icon-color="iconColor"
    :title="title"
    :description="description"
    :action-label="actionLabel"
    :action-to="actionTo"
    :action-icon="actionIcon"
    :compact="compact"
    @action="$emit('action')"
  >
    <template v-if="$slots.action" #action>
      <slot name="action" />
    </template>
  </AppEmptyState>
</template>

<script setup>
import { AppEmptyState } from '../ui/index.js'

defineProps({
  preset: { type: String, default: '' },
  icon: { type: String, default: '' },
  iconSize: { type: [Number, String], default: 56 },
  iconColor: { type: String, default: 'primary' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionTo: { type: String, default: '' },
  actionIcon: { type: String, default: 'mdi-plus' },
  compact: { type: Boolean, default: false },
})

defineEmits(['action'])
</script>
