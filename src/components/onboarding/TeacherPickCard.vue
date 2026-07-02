<template>
  <v-card
    class="teacher-pick glass-card pa-4"
    :class="{ 'teacher-pick--selected': selected }"
    variant="flat"
    @click="$emit('select')"
  >
    <div class="d-flex align-center gap-3">
      <TeacherAvatar :name="teacher.full_name" :image-url="teacher.image_url" :size="56" />
      <div class="text-start flex-grow-1 min-width-0">
        <div class="text-subtitle-2 font-weight-bold text-truncate">{{ teacher.full_name }}</div>
        <v-chip size="x-small" variant="tonal" color="secondary" class="mt-1 mb-1">
          {{ teacher.subject_name }}
        </v-chip>
        <div class="d-flex align-center gap-2 mt-1">
          <div class="rating-pill">
            <v-icon size="14" color="warning">mdi-star</v-icon>
            <span class="text-caption font-weight-bold">{{ formattedRating }}</span>
          </div>
          <span class="text-caption text-medium-emphasis">{{ studentCountLabel }}</span>
        </div>
        <p v-if="teacher.bio" class="text-caption text-medium-emphasis mb-0 mt-2 line-clamp-2">
          {{ teacher.bio }}
        </p>
      </div>
      <div class="teacher-pick__check">
        <v-icon v-if="selected" color="secondary" size="28">mdi-check-circle</v-icon>
        <v-icon v-else size="22" color="grey-darken-1">mdi-circle-outline</v-icon>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TeacherAvatar from './TeacherAvatar.vue'

const props = defineProps({
  teacher: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

defineEmits(['select'])

const { t } = useI18n()

const formattedRating = computed(() => {
  const r = Number(props.teacher.rating)
  return Number.isFinite(r) ? r.toFixed(1) : t('parent.common.emDash')
})

const studentCountLabel = computed(() => {
  const count = Number(props.teacher.student_count) || 0
  if (count === 1) return t('auth.onboarding.teacherPick.studentCountOne')
  return t('auth.onboarding.teacherPick.studentCount', { count })
})
</script>

<style scoped>
.teacher-pick {
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  transition:
    transform 0.28s cubic-bezier(0.34, 1.2, 0.64, 1),
    border-color 0.28s ease,
    box-shadow 0.28s ease;
}

.teacher-pick:hover {
  transform: translateY(-2px);
  border-color: rgba(124, 108, 240, 0.35) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 24px rgba(124, 108, 240, 0.12) !important;
}

.teacher-pick--selected {
  border-color: rgba(34, 211, 238, 0.5) !important;
  box-shadow:
    0 0 28px rgba(34, 211, 238, 0.18),
    inset 0 0 0 1px rgba(34, 211, 238, 0.12) !important;
}

.rating-pill {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.min-width-0 {
  min-width: 0;
}

.teacher-pick__check {
  flex-shrink: 0;
}
</style>
