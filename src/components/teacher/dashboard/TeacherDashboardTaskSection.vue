<template>
  <AppSection
    :class="['teacher-home__section', sectionClass]"
    :eyebrow="eyebrow"
    :title="title"
    :subtitle="subtitle"
    spacing="sm"
    :divider="false"
  >
    <TeacherEmptyStateCard
      v-if="!items.length"
      compact
      :icon="emptyIcon"
      :title="emptyTitle"
      :description="emptyDescription"
    />

    <div v-else class="teacher-dashboard-tasks">
      <article
        v-for="item in items"
        :key="item.id"
        class="teacher-dashboard-task"
      >
        <TeacherWarningCard
          :variant="item.variant"
          :title="item.title"
          :message="item.message"
        />
        <TeacherButton
          v-if="item.actionLabel"
          :variant="item.actionVariant || 'primary'"
          size="small"
          :to="item.to"
          :prepend-icon="item.actionIcon"
        >
          {{ item.actionLabel }}
        </TeacherButton>
      </article>
    </div>
  </AppSection>
</template>

<script setup>
import { AppSection } from '../../ui/index.js'
import {
  TeacherButton,
  TeacherEmptyStateCard,
  TeacherWarningCard,
} from '../design-system/index.js'

defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  sectionClass: { type: String, default: '' },
  items: { type: Array, default: () => [] },
  emptyIcon: { type: String, default: 'mdi-check-circle-outline' },
  emptyTitle: { type: String, default: '' },
  emptyDescription: { type: String, default: '' },
})
</script>
