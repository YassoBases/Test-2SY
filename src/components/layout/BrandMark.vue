<template>
  <div class="brand-mark text-center">
    <EduSparkBrandIcon context="sidebar" class="brand-mark__logo mb-2" />
    <div class="text-caption text-medium-emphasis">{{ displayTagline }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

const props = defineProps({
  tagline: { type: String, default: '' },
})

const { t } = useI18n()
const displayTagline = computed(() => props.tagline || t('common.brand.tagline'))
</script>

<style scoped>
.brand-mark {
  padding: 0 4px;
}

.brand-mark__logo {
  margin-bottom: 8px;
}
</style>
