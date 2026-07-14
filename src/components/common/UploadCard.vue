<template>
  <section class="upload-card pa-5 pa-md-8" :class="opaque ? 'upload-card--opaque' : 'glass-card glass-card--elevated'">
    <div v-if="showHeader" class="d-flex align-center justify-space-between flex-wrap gap-3 mb-6">
      <div class="d-flex align-center gap-3">
        <v-avatar size="44" class="eduspark-gradient" rounded="lg">
          <v-icon color="white">mdi-file-pdf-box</v-icon>
        </v-avatar>
        <div>
          <div class="text-h6 font-weight-bold">{{ resolvedTitle }}</div>
          <div class="text-caption text-medium-emphasis">{{ resolvedSubtitle }}</div>
        </div>
      </div>
      <v-chip v-if="resolvedBadge" color="secondary" variant="tonal" size="small" prepend-icon="mdi-star-four-points">
        {{ resolvedBadge }}
      </v-chip>
    </div>
    <PdfUploadBox
      :file="file"
      :uploading="uploading"
      :progress="progress"
      :error="error"
      @select="$emit('select', $event)"
      @remove="$emit('remove')"
      @dismiss-error="$emit('dismiss-error')"
    />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import PdfUploadBox from '../teacher/PdfUploadBox.vue'

const props = defineProps({
  file: { type: Object, default: null },
  uploading: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  error: { type: String, default: null },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  badge: { type: String, default: '' },
  showHeader: { type: Boolean, default: true },
  opaque: { type: Boolean, default: false },
})

defineEmits(['select', 'remove', 'dismiss-error'])

const { t } = useI18n()

const resolvedTitle = computed(() => props.title || t('common.upload.lessonFile'))
const resolvedSubtitle = computed(() => props.subtitle || t('common.upload.pdfSubtitle'))
const resolvedBadge = computed(() => props.badge || t('common.upload.mainFocus'))
</script>

<style scoped>
.upload-card--opaque {
  background: rgb(var(--v-theme-surface)) !important;
  border: 1px solid rgba(var(--v-border-color), 0.14);
  border-radius: 12px;
}
</style>
