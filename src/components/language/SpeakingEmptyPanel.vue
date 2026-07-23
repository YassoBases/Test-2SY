<template>
  <v-card
    class="spk-empty glass-card"
    variant="flat"
    role="status"
    :aria-label="title"
  >
    <v-icon
      class="spk-empty__icon"
      :color="iconColor"
      :size="compact ? 36 : 44"
      aria-hidden="true"
    >
      {{ icon }}
    </v-icon>
    <div class="spk-empty__title">{{ title }}</div>
    <p v-if="description" class="spk-empty__body text-body-2 mb-0">{{ description }}</p>
    <div v-if="actionLabel || $slots.action" class="mt-4">
      <slot name="action">
        <v-btn
          color="primary"
          class="em-btn em-btn--primary spk-pressable"
          :prepend-icon="actionIcon"
          :loading="loading"
          :aria-label="actionLabel"
          @click="$emit('action')"
        >
          {{ actionLabel }}
        </v-btn>
      </slot>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'mdi-information-outline' },
  iconColor: { type: String, default: 'primary' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionIcon: { type: String, default: 'mdi-play' },
  loading: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})

defineEmits(['action'])
</script>
