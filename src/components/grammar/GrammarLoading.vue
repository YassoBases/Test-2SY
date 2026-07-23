<template>
  <div class="grammar-loading">
    <v-card v-if="generating" class="glass-card pa-8" variant="flat">
      <LearningLoader title="Creating your Grammar lesson…" icon="mdi-pencil-outline" />
    </v-card>
    <LoadingState v-else variant="cards" :count="3" />
  </div>
</template>

<script setup>
import LoadingState from '../common/LoadingState.vue'
import LearningLoader from '../language/LearningLoader.vue'

defineProps({
  generating: { type: Boolean, default: false },
})
</script>
