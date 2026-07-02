<template>
  <div class="student-selector-bar d-flex align-center flex-wrap gap-3">
    <v-select
      :model-value="modelValue"
      :items="items"
      item-title="label"
      item-value="value"
      density="comfortable"
      variant="outlined"
      hide-details
      class="student-selector"
      prepend-inner-icon="mdi-account-child"
      @update:model-value="$emit('update:modelValue', $event)"
    >
      <template #selection="{ item }">
        <span class="font-weight-bold">{{ item.raw.shortName }}</span>
      </template>
    </v-select>

    <v-btn
      size="small"
      variant="tonal"
      color="primary"
      prepend-icon="mdi-plus"
      :to="linkRoute"
    >
      {{ t('parent.common.linkStudent') }}
    </v-btn>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../../constants/app.js'

const props = defineProps({
  students: { type: Array, default: () => [] },
  modelValue: { type: Number, default: null },
})

defineEmits(['update:modelValue'])

const { t } = useI18n()

const linkRoute = ROUTES.PARENT_LINK

const items = computed(() =>
  props.students.map((s) => ({
    value: s.id,
    label: s.name,
    shortName: displayName(s.name),
  })),
)

function displayName(name) {
  const parts = String(name || '').trim().split(/\s+/)
  if (parts.length <= 2) return name
  return `${parts[0]} ${parts[parts.length - 1]}`
}
</script>

<style scoped>
.student-selector {
  min-width: 200px;
  max-width: 280px;
}

.student-selector-bar {
  margin-bottom: 1rem;
}
</style>
