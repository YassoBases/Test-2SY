<template>
  <div class="parent-portal-page slide-up-enter-active" :style="{ maxWidth }">
    <ParentStudentSelector
      v-if="hasStudents && !loadingStudents"
      :students="students"
      :model-value="selectedStudentId"
      class="mb-2"
      @update:model-value="$emit('select-student', $event)"
    />

    <PageHeader
      :eyebrow="eyebrow || t('parent.shell.eyebrow')"
      :eyebrow-icon="eyebrowIcon"
      :title="title"
      :subtitle="subtitle"
      :gradient-title="gradientTitle"
    />

    <ParentStudentContextBar v-if="hasStudents && studentContext" :context="studentContext" />

    <v-alert
      v-if="studentsError"
      type="warning"
      variant="tonal"
      class="mb-5 rounded-lg"
      closable
      @click:close="$emit('clear-students-error')"
    >
      {{ studentsError }}
    </v-alert>

    <v-skeleton-loader v-if="loadingStudents" type="card" class="mb-6 rounded-lg" />

    <template v-else-if="!hasStudents">
      <v-alert type="info" variant="tonal" class="mb-5 rounded-lg">
        {{ t('parent.shell.noStudentsLinked') }}
      </v-alert>
      <v-row justify="center">
        <v-col cols="12" md="8" lg="6">
          <ParentLinkStudentForm
            :linking="linking"
            :link-error="linkError"
            :link-success="linkSuccess"
            :has-students="false"
            :show-dashboard-link="false"
            @submit="$emit('link', $event)"
            @clear-error="$emit('clear-link-error')"
            @clear-success="$emit('clear-link-success')"
          />
        </v-col>
      </v-row>
    </template>

    <template v-else>
      <v-alert
        v-if="loadError"
        type="error"
        variant="tonal"
        class="mb-5 rounded-lg"
        closable
        @click:close="$emit('clear-load-error')"
      >
        {{ loadError }}
      </v-alert>

      <v-skeleton-loader v-if="loading" type="article" class="mb-6 rounded-lg" />

      <slot v-else />
    </template>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import PageHeader from '../../common/PageHeader.vue'
import ParentLinkStudentForm from '../ParentLinkStudentForm.vue'
import ParentStudentSelector from './ParentStudentSelector.vue'
import ParentStudentContextBar from './ParentStudentContextBar.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  eyebrowIcon: { type: String, default: 'mdi-shield-heart' },
  gradientTitle: { type: Boolean, default: false },
  maxWidth: { type: String, default: '1200px' },
  students: { type: Array, default: () => [] },
  selectedStudentId: { type: Number, default: null },
  studentContext: { type: Object, default: null },
  hasStudents: { type: Boolean, default: false },
  loadingStudents: { type: Boolean, default: false },
  studentsError: { type: String, default: '' },
  linking: { type: Boolean, default: false },
  linkError: { type: String, default: '' },
  linkSuccess: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
})

defineEmits([
  'select-student',
  'link',
  'clear-students-error',
  'clear-link-error',
  'clear-link-success',
  'clear-load-error',
])

const { t } = useI18n()
</script>

<style scoped>
.parent-portal-page {
  margin-inline: auto;
}
</style>
