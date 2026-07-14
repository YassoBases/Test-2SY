<template>
  <div v-if="hasAny" class="speaking-skills">
    <v-row dense>
      <v-col v-if="weakSkills.length" cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <div class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
            <v-icon size="20" color="warning" aria-hidden="true">mdi-alert-circle-outline</v-icon>
            {{ t('student.languages.speakingJourney.skills.weak') }}
          </div>
          <div class="skill-cards">
            <article v-for="(item, i) in weakSkills" :key="`w-${i}`" class="skill-card pa-3 rounded-lg">
              <div class="text-body-2 font-weight-medium mb-1">{{ item.label || '—' }}</div>
              <div v-if="item.improvement_focus" class="text-caption text-medium-emphasis">
                {{ item.improvement_focus }}
              </div>
            </article>
          </div>
        </v-card>
      </v-col>
      <v-col v-if="improvingSkills.length" cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <div class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
            <v-icon size="20" color="success" aria-hidden="true">mdi-trending-up</v-icon>
            {{ t('student.languages.speakingJourney.skills.improving') }}
          </div>
          <div class="skill-cards">
            <article v-for="(item, i) in improvingSkills" :key="`i-${i}`" class="skill-card pa-3 rounded-lg">
              <div class="text-body-2 font-weight-medium mb-1">{{ item.label || '—' }}</div>
              <div v-if="item.improvement_focus" class="text-caption text-medium-emphasis">
                {{ item.improvement_focus }}
              </div>
            </article>
          </div>
        </v-card>
      </v-col>
      <v-col v-if="retentionNeeded.length" cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <div class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
            <v-icon size="20" color="primary" aria-hidden="true">mdi-brain</v-icon>
            {{ t('student.languages.speakingJourney.skills.retention') }}
          </div>
          <div class="skill-cards">
            <article v-for="(item, i) in retentionNeeded" :key="`r-${i}`" class="skill-card pa-3 rounded-lg">
              <div class="text-body-2 font-weight-medium mb-1">{{ item.label || '—' }}</div>
              <div v-if="item.improvement_focus" class="text-caption text-medium-emphasis">
                {{ item.improvement_focus }}
              </div>
            </article>
          </div>
        </v-card>
      </v-col>
      <v-col v-if="transferNeeded.length" cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <div class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center gap-2">
            <v-icon size="20" color="secondary" aria-hidden="true">mdi-swap-horizontal</v-icon>
            {{ t('student.languages.speakingJourney.skills.transfer') }}
          </div>
          <div class="skill-cards">
            <article v-for="(item, i) in transferNeeded" :key="`t-${i}`" class="skill-card pa-3 rounded-lg">
              <div class="text-body-2 font-weight-medium mb-1">{{ item.label || '—' }}</div>
              <div v-if="item.improvement_focus" class="text-caption text-medium-emphasis">
                {{ item.improvement_focus }}
              </div>
            </article>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  weakSkills: { type: Array, default: () => [] },
  improvingSkills: { type: Array, default: () => [] },
  retentionNeeded: { type: Array, default: () => [] },
  transferNeeded: { type: Array, default: () => [] },
})

const { t } = useI18n()

const hasAny = computed(
  () =>
    props.weakSkills.length +
      props.improvingSkills.length +
      props.retentionNeeded.length +
      props.transferNeeded.length >
    0,
)
</script>

<style scoped>
.skill-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skill-card {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.h-100 {
  height: 100%;
}
</style>
