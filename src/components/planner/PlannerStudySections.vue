<template>
  <div class="planner-sections page-stack">
    <section class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.todayPlanTitle') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('common.planner.todayPlanSubtitle') }}</p>
      </div>
      <v-card class="glass-card glass-card--solid pa-4" variant="flat">
        <PlannerSlotList
          :slots="todaySlots"
          empty-icon="mdi-weather-sunny"
          :empty-text="t('common.planner.todayEmpty')"
          @complete="$emit('complete', $event)"
        />
      </v-card>
    </section>

    <section class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.weekPlanTitle') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('common.planner.weekPlanSubtitle') }}</p>
      </div>
      <v-card class="glass-card glass-card--solid pa-4" variant="flat">
        <PlannerSlotList
          :slots="weekSlots"
          empty-icon="mdi-calendar-week"
          :empty-text="t('common.planner.weekEmpty')"
          @complete="$emit('complete', $event)"
        />
      </v-card>
    </section>

    <section class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.aiRecommendationsTitle') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('common.planner.aiRecommendationsSubtitle') }}</p>
      </div>
      <v-card class="glass-card glass-card--solid pa-4" variant="flat">
        <ul v-if="aiRecommendations.length" class="planner-rec-list mb-0">
          <li v-for="(line, i) in aiRecommendations" :key="i" class="planner-rec-list__item">
            <v-icon size="18" color="secondary" class="me-2">mdi-robot-happy-outline</v-icon>
            <span>{{ line }}</span>
          </li>
        </ul>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">
          {{ t('common.planner.recommendationsEmpty') }}
        </p>
      </v-card>
    </section>

    <section class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.studySections.upcomingTasksTitle') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('common.planner.studySections.upcomingTasksSubtitle') }}</p>
      </div>
      <v-card class="glass-card glass-card--solid pa-4" variant="flat">
        <div v-if="deadlines.length" class="d-flex flex-column gap-2">
          <div
            v-for="item in deadlines"
            :key="item.id"
            class="planner-deadline d-flex align-center gap-3 pa-3 rounded-lg"
          >
            <v-icon :color="item.color" size="22">{{ item.icon }}</v-icon>
            <div class="min-w-0 flex-grow-1">
              <div class="text-body-2 font-weight-medium">{{ item.title }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.subtitle }}</div>
            </div>
          </div>
        </div>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">
          {{ t('common.planner.studySections.upcomingTasksEmpty') }}
        </p>
      </v-card>
    </section>

    <section class="section-block">
      <div class="section-block__head">
        <h3 class="section-block__title">{{ t('common.planner.studySections.suggestedLessonsTitle') }}</h3>
        <p class="section-block__subtitle mb-0">{{ t('common.planner.studySections.suggestedLessonsSubtitle') }}</p>
      </div>
      <v-card class="glass-card glass-card--solid pa-4" variant="flat">
        <div v-if="suggestedLessons.length" class="d-flex flex-column gap-2">
          <div
            v-for="item in suggestedLessons"
            :key="item.id"
            class="planner-suggest d-flex align-center justify-space-between gap-3 pa-3 rounded-lg"
          >
            <div class="d-flex align-center gap-3 min-w-0">
              <v-icon color="primary" size="22">mdi-book-open-page-variant</v-icon>
              <div class="min-w-0">
                <div class="text-body-2 font-weight-medium text-truncate">{{ item.title }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.reason }}</div>
              </div>
            </div>
            <v-btn
              v-if="item.to"
              size="small"
              variant="tonal"
              color="primary"
              rounded="lg"
              :to="item.to"
            >
              {{ t('common.planner.studySections.followUp') }}
            </v-btn>
          </div>
        </div>
        <p v-else class="text-body-2 text-medium-emphasis mb-0">
          {{ t('common.planner.studySections.suggestedLessonsEmpty') }}
        </p>
      </v-card>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import PlannerSlotList from './PlannerSlotList.vue'
import { partitionSchedule, upcomingDeadlines } from '../../utils/plannerSchedule.js'
import { ROUTES } from '../../constants/app.js'

const props = defineProps({
  schedule: { type: Array, default: () => [] },
  reasoning: { type: Array, default: () => [] },
  insights: { type: Array, default: () => [] },
  recommendations: { type: Array, default: () => [] },
  profile: { type: Object, default: () => ({}) },
  lifeEvents: { type: Array, default: () => [] },
  courses: { type: Array, default: () => [] },
})

defineEmits(['complete'])

const { t } = useI18n()

const partitioned = computed(() => partitionSchedule(props.schedule))
const todaySlots = computed(() => partitioned.value.today)
const weekSlots = computed(() => partitioned.value.thisWeek)

const aiRecommendations = computed(() => {
  if (props.recommendations?.length) {
    return props.recommendations.map((r) => `${r.priority_icon || ''} ${r.text}`.trim())
  }
  const lines = [...(props.insights || []), ...(props.reasoning || [])]
  return [...new Set(lines.map((s) => String(s).trim()).filter(Boolean))].slice(0, 6)
})

const deadlines = computed(() => upcomingDeadlines(props.lifeEvents, props.schedule))

const suggestedLessons = computed(() => {
  const out = []
  const weak = props.profile?.weak_subjects || []
  const unlocked = (props.courses || []).filter((c) => c.unlocked)

  for (const subject of weak) {
    const course = unlocked.find(
      (c) =>
        c.subject_name?.includes(subject) ||
        subject.includes(c.subject_name) ||
        c.subject_name === subject,
    )
    if (course) {
      out.push({
        id: `weak-${course.id}`,
        title: course.subject_name,
        reason: t('common.planner.reasonFocus'),
        to: ROUTES.STUDENT_COURSE(course.id),
      })
    } else {
      out.push({
        id: `weak-${subject}`,
        title: subject,
        reason: t('common.planner.reasonWeak'),
        to: ROUTES.STUDENT_COURSES,
      })
    }
  }

  for (const slot of props.schedule) {
    if (slot.status !== 'planned') continue
    if (out.some((x) => x.title === slot.subject)) continue
    out.push({
      id: `slot-${slot.id}`,
      title: slot.subject,
      reason: slot.reasoning || t('common.planner.reasonSuggested'),
      to: null,
    })
    if (out.length >= 6) break
  }

  return out.slice(0, 6)
})
</script>

<style scoped>
.planner-rec-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.planner-rec-list__item {
  display: flex;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid rgba(124, 108, 240, 0.1);
  font-size: 0.9rem;
  line-height: 1.45;
}

.planner-rec-list__item:last-child {
  border-bottom: none;
}

.planner-deadline,
.planner-suggest {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(124, 108, 240, 0.12);
}
</style>
