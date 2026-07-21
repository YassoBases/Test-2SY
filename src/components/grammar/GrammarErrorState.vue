<template>
  <v-card class="glass-card pa-6 text-center" variant="flat">
    <v-icon size="48" color="warning" class="mb-3">mdi-alert-circle-outline</v-icon>
    <h3 class="text-h6 font-weight-bold mb-2">Something went wrong</h3>
    <p class="text-body-2 text-medium-emphasis mb-4">{{ message }}</p>
    <v-btn
      color="secondary"
      variant="flat"
      prepend-icon="mdi-refresh"
      :loading="loading"
      :disabled="loading"
      @click="$emit('retry')"
    >
      Try again
    </v-btn>
  </v-card>
</template>

<script setup>
defineProps({
  message: { type: String, required: true },
  loading: { type: Boolean, default: false },
})
defineEmits(['retry'])
</script>
