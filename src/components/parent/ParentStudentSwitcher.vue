<template>
  <v-card class="glass-card pa-4 pa-md-5 mb-6 student-switcher" variant="flat">
    <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-3">
      <div class="d-flex align-center gap-2">
        <v-icon color="secondary">mdi-account-switch</v-icon>
        <span class="text-subtitle-1 font-weight-bold">{{ t('parent.link.linkedStudents') }}</span>
        <v-chip size="small" variant="tonal" color="primary">{{ students.length }}</v-chip>
      </div>
      <v-btn
        size="small"
        variant="tonal"
        color="primary"
        prepend-icon="mdi-plus"
        :to="linkRoute"
      >
        {{ t('parent.link.linkStudent') }}
      </v-btn>
    </div>

    <v-chip-group
      :model-value="modelValue"
      mandatory
      selected-class="student-chip--active"
      class="student-chips"
      @update:model-value="$emit('update:modelValue', $event)"
    >
      <v-chip
        v-for="student in students"
        :key="student.id"
        :value="student.id"
        filter
        variant="outlined"
        size="large"
        class="student-chip"
      >
        <template #prepend>
          <v-avatar size="28" class="eduspark-gradient me-1">
            <span class="text-caption font-weight-bold text-white">{{ initials(student.name) }}</span>
          </v-avatar>
        </template>
        {{ displayName(student.name) }}
      </v-chip>
    </v-chip-group>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ROUTES } from '../../constants/app.js'

defineProps({
  students: { type: Array, default: () => [] },
  modelValue: { type: Number, default: null },
})

defineEmits(['update:modelValue'])

const { t } = useI18n()

const linkRoute = ROUTES.PARENT_LINK

function initials(name) {
  const parts = String(name || '?').split(' ')
  return parts.slice(0, 2).map((p) => p[0]).join('')
}

function displayName(name) {
  const parts = String(name || '').trim().split(/\s+/)
  if (parts.length <= 2) return name
  return `${parts[0]} ${parts[parts.length - 1]}`
}
</script>

<style scoped>
.student-chip--active {
  border-color: rgb(var(--v-theme-primary)) !important;
  background: rgba(124, 108, 240, 0.12) !important;
}

.student-chips {
  flex-wrap: wrap;
}
</style>
