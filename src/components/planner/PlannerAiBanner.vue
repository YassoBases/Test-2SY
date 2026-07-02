<template>
  <v-card class="planner-ai-banner mb-5 pa-4 pa-md-5" variant="flat">
    <div class="d-flex align-center gap-3 flex-wrap">
      <div class="pulse-ring">
        <EduSparkBrandIcon context="loading" />
      </div>
      <div class="flex-grow-1">
        <p class="text-caption mb-1" style="color: var(--em-cyan)">{{ t('common.planner.aiAssistant') }}</p>
        <p class="text-body-1 font-weight-medium mb-0">{{ resolvedMessage }}</p>
      </div>
      <v-chip v-for="tag in resolvedTags" :key="tag" size="small" variant="outlined" class="neon-chip">
        {{ tag }}
      </v-chip>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EduSparkBrandIcon from '../common/EduSparkBrandIcon.vue'

const props = defineProps({
  message: { type: String, default: '' },
  tags: { type: Array, default: null },
})

const { t, tm } = useI18n()

const resolvedMessage = computed(() => props.message || t('common.planner.aiBannerMessage'))
const resolvedTags = computed(() => {
  if (props.tags?.length) return props.tags
  const tagKeys = ['weakSubjects', 'exams', 'rest', 'nightMorning']
  return tagKeys.map((key) => t(`common.planner.tags.${key}`))
})
</script>

<style scoped>
.planner-ai-banner {
  background: linear-gradient(90deg, rgba(124, 108, 240, 0.2), rgba(34, 211, 238, 0.1)) !important;
  border: 1px solid rgba(34, 211, 238, 0.3) !important;
  animation: banner-glow 4s ease-in-out infinite;
}

.pulse-ring {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--em-purple), var(--em-cyan));
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.4);
}

.neon-chip {
  border-color: rgba(34, 211, 238, 0.4) !important;
  color: var(--em-cyan) !important;
}

@keyframes banner-glow {
  0%, 100% { box-shadow: 0 0 24px rgba(124, 108, 240, 0.15); }
  50% { box-shadow: 0 0 36px rgba(34, 211, 238, 0.2); }
}
</style>
