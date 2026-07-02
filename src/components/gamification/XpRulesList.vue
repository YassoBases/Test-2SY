<template>
  <div class="xp-rules">
    <div v-for="group in groupedRules" :key="group.key" class="xp-rules__group mb-4">
      <div class="text-subtitle-2 font-weight-bold mb-2">{{ group.label }}</div>
      <div
        v-for="rule in group.items"
        :key="`${group.key}-${rule.label}`"
        class="xp-rules__row d-flex align-center justify-space-between pa-3 rounded-lg mb-2"
      >
        <span class="text-body-2">{{ rule.label }}</span>
        <v-chip size="small" color="secondary" variant="tonal">+{{ rule.xp }} XP</v-chip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  rules: {
    type: Array,
    default: () => [],
  },
})

const { t } = useI18n()

const groupedRules = computed(() => {
  const map = new Map()
  for (const rule of props.rules) {
    const key = rule.category || 'other'
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(rule)
  }
  return [...map.entries()].map(([key, items]) => ({
    key,
    label: t(`student.achievements.xpCategories.${key}`),
    items,
  }))
})
</script>

<style scoped>
.xp-rules__row {
  background: rgba(124, 108, 240, 0.06);
  border: 1px solid rgba(124, 108, 240, 0.12);
}
</style>
