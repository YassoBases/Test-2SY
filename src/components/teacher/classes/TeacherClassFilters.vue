<template>
  <div class="teacher-class-filters" role="group" :aria-label="$t('teacher.grades.filterClasses')">
    <button
      type="button"
      class="teacher-class-filters__chip"
      :class="{ 'teacher-class-filters__chip--active': modelValue === 'all' }"
      @click="$emit('update:modelValue', 'all')"
    >
      {{ $t('common.all') }}
      <span v-if="counts.all != null" class="teacher-class-filters__count">{{ counts.all }}</span>
    </button>

    <button
      v-for="g in gradeOptions"
      :key="`grade-${g}`"
      type="button"
      class="teacher-class-filters__chip"
      :class="{ 'teacher-class-filters__chip--active': modelValue === `grade:${g}` }"
      @click="$emit('update:modelValue', `grade:${g}`)"
    >
      {{ $t('teacher.labels.gradeNumber', { grade: g }) }}
      <span class="teacher-class-filters__count">{{ counts[`grade:${g}`] ?? 0 }}</span>
    </button>

    <button
      v-for="subj in subjectOptions"
      :key="`subject-${subj.id}`"
      type="button"
      class="teacher-class-filters__chip"
      :class="{ 'teacher-class-filters__chip--active': modelValue === `subject:${subj.id}` }"
      @click="$emit('update:modelValue', `subject:${subj.id}`)"
    >
      {{ subj.name }}
      <span class="teacher-class-filters__count">{{ counts[`subject:${subj.id}`] ?? 0 }}</span>
    </button>

    <button
      type="button"
      class="teacher-class-filters__chip"
      :class="{ 'teacher-class-filters__chip--active': modelValue === 'published' }"
      @click="$emit('update:modelValue', 'published')"
    >
      {{ $t('teacher.status.published') }}
      <span class="teacher-class-filters__count">{{ counts.published ?? 0 }}</span>
    </button>

    <button
      type="button"
      class="teacher-class-filters__chip"
      :class="{ 'teacher-class-filters__chip--active': modelValue === 'draft' }"
      @click="$emit('update:modelValue', 'draft')"
    >
      {{ $t('teacher.status.draft') }}
      <span class="teacher-class-filters__count">{{ counts.draft ?? 0 }}</span>
    </button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

defineProps({
  modelValue: { type: String, default: 'all' },
  gradeOptions: { type: Array, default: () => [] },
  subjectOptions: { type: Array, default: () => [] },
  counts: { type: Object, default: () => ({}) },
})

defineEmits(['update:modelValue'])
</script>
