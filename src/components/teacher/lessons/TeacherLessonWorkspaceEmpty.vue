<template>
  <div class="lesson-workspace-empty">
    <span class="lesson-workspace-empty__icon" aria-hidden="true">
      <v-icon size="36">mdi-bookshelf</v-icon>
    </span>
    <h3 class="lesson-workspace-empty__title">{{ $t('teacher.lessons.emptyTitle') }}</h3>
    <p class="lesson-workspace-empty__desc">{{ $t('teacher.lessons.emptyHint') }}</p>
    <v-btn v-if="showAction" class="btn-glow" rounded="lg" @click="$emit('add')">
      <v-icon start>mdi-plus</v-icon>
      {{ $t('teacher.actions.addLesson') }}
    </v-btn>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  showAction: { type: Boolean, default: true },
})

defineEmits(['add'])
</script>
