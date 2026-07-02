<template>
  <v-card class="parent-ai-banner neon-banner pa-5 pa-md-6 mb-6" variant="flat">
    <div class="d-flex align-start gap-4 flex-wrap">
      <v-avatar size="52" class="banner-avatar">
        <v-icon color="white" size="28">mdi-creation</v-icon>
      </v-avatar>
      <div class="flex-grow-1">
        <p class="text-caption text-medium-emphasis mb-1">{{ t('parent.insights.banner.eyebrow') }}</p>
        <h2 class="text-h6 font-weight-bold mb-2 neon-text">
          {{ t('parent.insights.banner.title', { name: childName }) }}
        </h2>
        <p v-if="topInsight" class="text-body-2 mb-0 banner-insight">{{ topInsight }}</p>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">
          {{ t('parent.insights.banner.hint') }}
        </p>
      </div>
      <v-chip color="warning" variant="tonal" prepend-icon="mdi-eye-lock" class="read-only-chip">
        {{ t('parent.insights.banner.parentMode') }}
      </v-chip>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  childName: { type: String, default: '' },
  insights: { type: Array, default: () => [] },
})

const { t } = useI18n()

const childName = computed(() => props.childName || t('parent.insights.banner.studentFallback'))
const topInsight = computed(() => props.insights[0]?.text ?? null)
</script>

<style scoped>
.parent-ai-banner {
  background: linear-gradient(135deg, rgba(124, 108, 240, 0.18) 0%, rgba(34, 211, 238, 0.08) 50%, rgba(15, 22, 45, 0.6) 100%) !important;
  border: 1px solid rgba(34, 211, 238, 0.25) !important;
  box-shadow: 0 0 40px rgba(124, 108, 240, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}

.banner-avatar {
  background: linear-gradient(135deg, var(--em-purple), var(--em-cyan));
  box-shadow: var(--em-glow-cyan);
}

.neon-text {
  background: linear-gradient(90deg, #e8ecf4, var(--em-cyan));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.banner-insight {
  border-inline-start: 3px solid var(--em-cyan);
  padding-inline-start: 12px;
  line-height: 1.6;
}
</style>
