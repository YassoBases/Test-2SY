<template>
  <AppSection
    class="teacher-home__section teacher-home__section--priorities"
    :eyebrow="$t('teacher.dashboard.today')"
    :title="$t('teacher.dashboard.priorities')"
    :subtitle="$t('teacher.dashboard.prioritiesDesc')"
    spacing="sm"
    :divider="false"
  >
    <div class="teacher-inbox">
      <template v-if="items.length">
        <component
          :is="item.to ? 'router-link' : 'div'"
          v-for="item in items"
          :key="item.id"
          :to="item.to || undefined"
          class="teacher-priority"
          :class="item.tone ? `teacher-priority--${item.tone}` : ''"
        >
          <span class="teacher-priority__icon" aria-hidden="true">
            <v-icon size="17">{{ item.icon }}</v-icon>
          </span>
          <div class="teacher-priority__body">
            <span class="teacher-priority__label">{{ item.label }}</span>
            <span v-if="item.detail" class="teacher-priority__detail">{{ item.detail }}</span>
          </div>
          <span v-if="item.actionLabel" class="teacher-priority__action">{{ item.actionLabel }}</span>
          <v-icon v-else-if="item.to" size="16" class="teacher-priority__chevron">mdi-chevron-left</v-icon>
        </component>
      </template>
      <div v-else class="teacher-inbox__empty">
        <v-icon size="18" class="teacher-inbox__empty-icon">mdi-check-circle-outline</v-icon>
        <span>{{ $t('teacher.dashboard.noUrgent') }}</span>
      </div>
    </div>
  </AppSection>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { AppSection } from '../../ui/index.js'

defineProps({
  items: { type: Array, default: () => [] },
})
</script>
