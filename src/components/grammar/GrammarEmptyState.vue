<template>
  <v-card class="glass-card pa-8 text-center" variant="flat">
    <v-icon size="48" color="secondary" class="mb-3">mdi-book-open-page-variant-outline</v-icon>
    <h3 class="text-h6 font-weight-bold mb-2">Ready to start today's grammar lesson.</h3>
    <p class="text-body-2 text-medium-emphasis mb-0 mx-auto grammar-empty__body">
      {{ message || 'Complete language placement to unlock your personalized Grammar path.' }}
    </p>
  </v-card>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' },
})
</script>

<style scoped>
.grammar-empty__body {
  max-width: 420px;
}
</style>
