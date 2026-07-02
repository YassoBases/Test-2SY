<template>
  <div class="planner-intelligence page-stack">
    <div v-if="streakDisplay" class="d-flex align-center gap-2 mb-4">
      <v-chip color="warning" variant="tonal" size="small">
        {{ streakDisplay }}
      </v-chip>
      <v-chip v-if="readOnly" size="x-small" variant="tonal">{{ t('common.planner.readOnly') }}</v-chip>
    </div>

    <p v-if="summary" class="text-body-2 text-medium-emphasis mb-4">{{ summary }}</p>

    <section v-if="weeklyPlan.length" class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.weeklyPlanTitle') }}</h3>
      </div>
      <PlannerWeeklyPlan :weekly-plan="weeklyPlan" :read-only="readOnly" />
    </section>

    <v-row>
      <v-col cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('common.planner.subjectAnalysisTitle') }}</h3>
          </div>
          <PlannerSubjectStrength :subjects="subjectAnalytics" />
        </section>
      </v-col>
      <v-col cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('common.planner.smartRecommendationsTitle') }}</h3>
          </div>
          <PlannerRecommendations :items="recommendations" />
        </section>
      </v-col>
    </v-row>

    <v-row v-if="completedTasks.length || missedTasks.length">
      <v-col v-if="completedTasks.length" cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('common.planner.completedTasksTitle') }}</h3>
          </div>
          <PlannerSlotList :slots="completedTasks" empty-text="" />
        </section>
      </v-col>
      <v-col v-if="missedTasks.length" cols="12" md="6">
        <section class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">{{ t('common.planner.missedTasksTitle') }}</h3>
          </div>
          <PlannerSlotList :slots="missedTasks" empty-text="" />
        </section>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import PlannerWeeklyPlan from './PlannerWeeklyPlan.vue'
import PlannerSubjectStrength from './PlannerSubjectStrength.vue'
import PlannerRecommendations from './PlannerRecommendations.vue'
import PlannerSlotList from './PlannerSlotList.vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  readOnly: { type: Boolean, default: true },
})

const { t } = useI18n()

const weeklyPlan = computed(() => props.data.weekly_plan || [])
const subjectAnalytics = computed(() => props.data.subject_analytics || [])
const recommendations = computed(() => props.data.recommendations || [])
const completedTasks = computed(() => props.data.completed_tasks || [])
const missedTasks = computed(() => props.data.missed_tasks || [])
const summary = computed(() => props.data.summary || '')
const streakDisplay = computed(() => {
  const days = props.data.streak?.current_streak_days ?? 0
  if (!days) return ''
  return t('common.planner.learningStreak', { days })
})
</script>
