<template>
  <AppCard
    class="catalog-card em-hover-lift home-stagger-item"
    :class="`catalog-card--${state}`"
    :style="{ '--stagger-delay': `${staggerDelay}ms` }"
    :interactive="true"
    padding="lg"
    :to="cardTo"
  >
    <div class="catalog-card__accent" aria-hidden="true" />

    <div class="catalog-card__body">
      <div class="catalog-card__avatar" :class="{ 'catalog-card__avatar--locked': state === 'locked' }">
        <TeacherAvatar
          :name="course.teacher_name"
          :image-url="teacherImage"
          :size="avatarSize"
        />
      </div>

      <h3 class="catalog-card__subject">{{ course.subject_name }}</h3>
      <p class="catalog-card__teacher-name">{{ course.teacher_name }}</p>
      <p class="catalog-card__progress">{{ progressText }}</p>

      <div class="catalog-card__divider" aria-hidden="true" />

      <div class="catalog-card__cta" :class="`catalog-card__cta--${state}`">
        <v-icon size="18" class="catalog-card__cta-icon">{{ ctaIcon }}</v-icon>
        <span>{{ ctaLabel }}</span>
      </div>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from '../../onboarding/TeacherAvatar.vue'
import { AppCard } from '../../ui/index.js'
import { ROUTES } from '../../../constants/app.js'
import { teacherImageFromEntity } from '../../../utils/teacherAvatar.js'

const { t } = useI18n()

const AVATAR_SIZE = 60

const props = defineProps({
  course: { type: Object, required: true },
  staggerDelay: { type: Number, default: 0 },
})

const teacherImage = computed(() => teacherImageFromEntity(props.course))
const avatarSize = AVATAR_SIZE

const state = computed(() => {
  if (!props.course.unlocked) return 'locked'
  if (props.course.progress_percent >= 100) return 'done'
  if (props.course.progress_percent > 0) return 'active'
  return 'ready'
})

const progressText = computed(() => {
  const total = props.course.lesson_count || 0
  const done = props.course.completed_lesson_count || 0

  if (!props.course.unlocked) {
    return total > 0 ? t('student.home.catalog.progress.zeroOf', { total }) : t('student.home.catalog.progress.unavailable')
  }
  if (total > 0) return t('student.home.catalog.progress.of', { done, total })
  if (done > 0) return t('student.home.catalog.progress.completedOnly', { done })
  return t('student.home.catalog.progress.notStarted')
})

const ctaLabel = computed(() => {
  const map = {
    locked: t('student.home.catalog.cta.locked'),
    done: t('student.home.catalog.cta.done'),
    active: t('student.home.catalog.cta.active'),
    ready: t('student.home.catalog.cta.ready'),
  }
  return map[state.value]
})

const ctaIcon = computed(() => {
  const map = {
    locked: 'mdi-lock-outline',
    done: 'mdi-check-circle-outline',
    active: 'mdi-play-circle-outline',
    ready: 'mdi-compass-outline',
  }
  return map[state.value]
})

const cardTo = computed(() =>
  props.course.unlocked
    ? ROUTES.STUDENT_COURSE(props.course.id)
    : ROUTES.STUDENT_SUBSCRIPTIONS,
)
</script>

<style scoped>
.catalog-card {
  position: relative;
  flex: 0 0 min(260px, 86vw);
  scroll-snap-align: start;
  min-height: 292px;
  overflow: hidden;
  border: 1px solid var(--em-border-subtle);
  touch-action: manipulation;
  transition:
    transform var(--em-duration-standard) var(--em-ease-out),
    box-shadow var(--em-duration-standard) var(--em-ease-out),
    border-color var(--em-duration-standard) var(--em-ease-out);
}

.catalog-card__accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(
    90deg,
    rgba(99, 102, 241, 0.15) 0%,
    rgba(99, 102, 241, 0.55) 40%,
    rgba(6, 182, 212, 0.45) 100%
  );
  opacity: 0.85;
}

.catalog-card--locked .catalog-card__accent {
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.45));
  opacity: 0.6;
}

.catalog-card--done .catalog-card__accent {
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.25), rgba(52, 211, 153, 0.55));
}

.catalog-card--locked {
  opacity: 0.92;
}

.catalog-card:hover {
  box-shadow: var(--em-shadow-lg), 0 8px 28px rgba(99, 102, 241, 0.08);
}

.catalog-card__body {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
  height: 100%;
  min-height: 244px;
  padding-top: 0.5rem;
}

.catalog-card__avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 4px;
}

.catalog-card__avatar--locked {
  opacity: 0.75;
  filter: saturate(0.7);
}

.catalog-card__subject {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  line-height: 1.2;
  color: var(--em-text);
  letter-spacing: -0.03em;
  max-width: 100%;
}

.catalog-card__teacher-name {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--em-text-muted);
  line-height: 1.35;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.catalog-card__progress {
  margin: 2px 0 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--em-text-helper);
  line-height: 1.35;
}

.catalog-card__divider {
  width: 100%;
  height: 1px;
  margin: 10px 0 4px;
  background: var(--em-border-subtle);
}

.catalog-card__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: auto;
  padding: 12px 16px;
  border-radius: var(--em-radius-sm);
  font-size: var(--em-text-sm);
  font-weight: 700;
  border: 1px solid transparent;
  transition:
    background var(--em-duration-fast) var(--em-ease-out),
    border-color var(--em-duration-fast) var(--em-ease-out);
}

.catalog-card__cta--active,
.catalog-card__cta--ready {
  background: rgba(99, 102, 241, 0.14);
  color: var(--em-primary);
}

.catalog-card__cta--done {
  background: rgba(52, 211, 153, 0.12);
  color: var(--em-success);
}

.catalog-card__cta--locked {
  background: rgba(251, 191, 36, 0.1);
  color: var(--em-warning);
}

.catalog-card:hover .catalog-card__cta--active,
.catalog-card:hover .catalog-card__cta--ready {
  background: rgba(99, 102, 241, 0.2);
}

.catalog-card__cta-icon {
  flex-shrink: 0;
}
</style>
