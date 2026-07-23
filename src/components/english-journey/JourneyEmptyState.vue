<template>
  <AppEmptyState
    :icon="icon"
    :title="title"
    :description="description"
    :action-label="actionLabel"
    :action-to="actionTo"
    @action="$emit('action')"
  />
</template>

<script setup>
import AppEmptyState from '../ui/AppEmptyState.vue'

defineProps({
  icon: { type: String, default: 'mdi-map-outline' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionTo: { type: String, default: '' },
})

defineEmits(['action'])
</script>
