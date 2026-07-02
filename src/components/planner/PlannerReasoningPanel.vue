<template>
  <v-card v-if="reasoning.length" class="glass-card pa-4" variant="flat">
    <div class="d-flex align-center gap-2 mb-3">
      <EduSparkBrandIcon context="inline" />
      <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ t('common.planner.reasoningTitle') }}</h3>
    </div>
    <v-list density="compact" class="bg-transparent">
      <v-list-item
        v-for="(line, i) in reasoning"
        :key="i"
        :prepend-icon="'mdi-check-circle-outline'"
        class="px-0"
      >
        <v-list-item-title class="text-body-2">{{ line }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

defineProps({
  reasoning: { type: Array, default: () => [] },
})

const { t } = useI18n()
</script>
