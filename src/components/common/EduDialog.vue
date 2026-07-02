<template>
  <v-dialog
    :model-value="modelValue"
    :max-width="maxWidth"
    :persistent="persistent"
    :fullscreen="fullscreen"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card class="edu-dialog-card glass-card--solid" variant="flat">
      <v-card-title v-if="title || $slots.title" class="d-flex align-center">
        <slot name="title">{{ title }}</slot>
        <v-spacer />
        <v-btn
          v-if="closable"
          icon="mdi-close"
          variant="text"
          size="small"
          class="em-btn--ghost"
          @click="$emit('update:modelValue', false)"
        />
      </v-card-title>
      <v-card-text>
        <slot />
      </v-card-text>
      <v-card-actions v-if="$slots.actions">
        <slot name="actions" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  maxWidth: { type: [Number, String], default: 560 },
  persistent: { type: Boolean, default: false },
  fullscreen: { type: Boolean, default: false },
  closable: { type: Boolean, default: true },
})

defineEmits(['update:modelValue'])
</script>
