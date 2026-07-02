<template>
  <v-btn-toggle
    :model-value="modelValue"
    mandatory
    color="secondary"
    variant="outlined"
    class="speaking-mode-toggle mb-4"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-btn value="exercises" size="small">
      <v-icon start size="18">mdi-format-list-bulleted</v-icon>
      Speaking exercises
    </v-btn>
    <v-btn value="conversation" size="small">
      <v-icon start size="18">mdi-robot-happy-outline</v-icon>
      Smart conversation
    </v-btn>
    <v-btn value="shadowing" size="small">
      <v-icon start size="18">mdi-account-voice</v-icon>
      Shadowing
    </v-btn>
    <v-btn value="scenarios" size="small">
      <v-icon start size="18">mdi-account-group-outline</v-icon>
      Scenarios
    </v-btn>
  </v-btn-toggle>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: 'exercises' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.speaking-mode-toggle {
  width: 100%;
  max-width: 720px;
  height: auto;
  background: transparent;
  gap: 10px;
  flex-wrap: wrap;
}
.speaking-mode-toggle :deep(.v-btn) {
  flex: 1 1 auto;
  border-radius: 10px !important;
  border: 1px solid rgba(var(--v-theme-secondary), 0.35) !important;
  white-space: nowrap;
}
</style>
