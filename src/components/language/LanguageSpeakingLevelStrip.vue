<template>
  <v-card class="glass-card level-strip pa-3 mb-4" variant="flat">
    <div class="d-flex align-center flex-wrap gap-3">
      <v-chip color="secondary" variant="tonal" size="small" prepend-icon="mdi-school-outline">
        Speaking level: {{ level || '—' }}
      </v-chip>
      <v-chip v-if='turnCount > 0' size="small" variant="outlined">
        {{ turnCount }} round
      </v-chip>
      <v-chip v-if="trend === 'up'" color="success" size="small" variant="tonal">↑ progress</v-chip>
      <v-chip v-else-if="trend === 'down'" color="warning" size="small" variant="tonal">↓ review</v-chip>
      <span v-if="baseline" class="text-caption text-medium-emphasis">
        Baseline (selection test): {{ baseline }}
      </span>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  level: { type: String, default: null },
  baseline: { type: String, default: null },
  turnCount: { type: Number, default: 0 },
  trend: { type: String, default: null },
  nextLevel: { type: String, default: null },
  masteryPercent: { type: Number, default: 0 },
})
</script>
