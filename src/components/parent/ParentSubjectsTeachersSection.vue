<template>
  <div>
    <v-alert v-if="!data?.has_grade" type="info" variant="tonal" class="mb-4">
      {{ t('parent.subjectsTeachers.noGrade') }}
    </v-alert>

    <template v-else>
      <div v-if="data?.grade_label" class="text-body-2 text-medium-emphasis mb-4">
        {{ t('parent.subjectsTeachers.gradeLabel', { grade: data.grade_label, name: data.student_name }) }}
      </div>

      <section class="mb-6">
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon color="success">mdi-book-check</v-icon>
          <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.subjectsTeachers.registered') }}</h3>
          <v-chip size="x-small" variant="tonal">{{ data?.enrolled_count ?? 0 }}</v-chip>
        </div>
        <v-row v-if="data?.enrolled?.length" dense>
          <v-col
            v-for="item in data.enrolled"
            :key="`enrolled-${item.course_id}`"
            cols="12"
            sm="6"
            lg="4"
          >
            <ParentSubjectTeacherCard
              :item="item"
              :contacting="contactingCourseId === item.course_id"
              @view-profile="$emit('view-profile', item)"
              @contact="$emit('contact', item)"
            />
          </v-col>
        </v-row>
        <v-card v-else class="glass-card pa-6 text-center" variant="flat">
          <v-icon size="40" color="medium-emphasis" class="mb-2">mdi-book-off-outline</v-icon>
          <p class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.subjectsTeachers.noRegistered') }}</p>
        </v-card>
      </section>

      <section>
        <div class="d-flex align-center gap-2 mb-3">
          <v-icon color="secondary">mdi-book-open-page-variant-outline</v-icon>
          <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.subjectsTeachers.available') }}</h3>
          <v-chip size="x-small" variant="tonal">{{ data?.available_count ?? 0 }}</v-chip>
        </div>
        <v-row v-if="data?.available?.length" dense>
          <v-col
            v-for="item in data.available"
            :key="`available-${item.course_id}`"
            cols="12"
            sm="6"
            lg="4"
          >
            <ParentSubjectTeacherCard
              :item="item"
              :contacting="contactingCourseId === item.course_id"
              @view-profile="$emit('view-profile', item)"
              @contact="$emit('contact', item)"
            />
          </v-col>
        </v-row>
        <v-card v-else class="glass-card pa-6 text-center" variant="flat">
          <p class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.subjectsTeachers.allEnrolled') }}</p>
        </v-card>
      </section>
    </template>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentSubjectTeacherCard from './ParentSubjectTeacherCard.vue'

defineProps({
  data: { type: Object, default: null },
  contactingCourseId: { type: Number, default: null },
})

defineEmits(['view-profile', 'contact'])

const { t } = useI18n()
</script>
