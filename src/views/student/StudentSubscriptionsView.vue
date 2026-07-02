<template>
  <div class="slide-up-enter-active">
    <PageHeader
      :eyebrow="t('student.subscriptions.header.eyebrow')"
      :title="t('student.subscriptions.header.title')"
      :subtitle="gradeSubtitle"
    />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-5 rounded-lg">{{ loadError }}</v-alert>
    <v-alert v-if="successMsg" type="success" variant="tonal" class="mb-5 rounded-lg">{{ successMsg }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <v-row class="mb-6">
        <v-col cols="6" sm="4">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold text-secondary">{{ catalog.unlocked_count }}</div>
            <div class="text-caption text-medium-emphasis">{{ t('student.subscriptions.kpi.unlocked') }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" sm="4">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-h5 font-weight-bold">{{ catalog.available_count }}</div>
            <div class="text-caption text-medium-emphasis">{{ t('student.subscriptions.kpi.available') }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="catalog.courses?.length">
        <v-col v-for="course in catalog.courses" :key="course.id" cols="12" md="6">
          <v-card class="glass-card h-100 d-flex flex-column" variant="flat">
            <v-card-text class="pa-5 flex-grow-1 d-flex flex-column">
              <div class="d-flex align-start gap-3 mb-3">
                <button
                  type="button"
                  class="teacher-profile-trigger pa-0"
                  :aria-label="t('student.subscriptions.teacherProfileAria', { name: course.teacher_name })"
                  @click="openTeacherProfile(course)"
                >
                  <TeacherAvatar
                    :name="course.teacher_name"
                    :image-url="course.teacher_image_url || course.avatar_url"
                    :size="52"
                  />
                </button>
                <div class="flex-grow-1 min-width-0">
                  <div class="text-subtitle-1 font-weight-bold">{{ course.subject_name }}</div>
                  <button
                    type="button"
                    class="teacher-name-link text-caption text-medium-emphasis pa-0"
                    @click="openTeacherProfile(course)"
                  >
                    {{ course.teacher_name }}
                  </button>
                </div>
                <v-chip v-if="course.unlocked" color="success" size="small" variant="flat">{{ t('student.subscriptions.status.unlocked') }}</v-chip>
                <v-chip v-else color="warning" size="small" variant="tonal">{{ t('student.subscriptions.status.locked') }}</v-chip>
              </div>

              <v-btn
                variant="text"
                size="small"
                color="secondary"
                class="mb-2 px-0 align-self-start"
                prepend-icon="mdi-account-details-outline"
                @click="openTeacherProfile(course)"
              >
                {{ t('student.subscriptions.teacherProfile') }}
              </v-btn>

              <div class="text-h6 font-weight-bold text-secondary mb-3">
                {{ formatSyrianPrice(course.price) }}
              </div>

              <p class="text-body-2 text-medium-emphasis mb-3 flex-grow-1">
                {{ course.subscription_benefits }}
              </p>

              <div class="d-flex flex-wrap gap-2 mb-4">
                <v-chip v-if="course.video_count" size="x-small" variant="tonal">{{ t('student.subscriptions.chips.video', { n: course.video_count }) }}</v-chip>
                <v-chip v-if="course.pdf_count" size="x-small" variant="tonal">{{ t('student.subscriptions.chips.pdf', { n: course.pdf_count }) }}</v-chip>
                <v-chip v-if="course.homework_count" size="x-small" variant="tonal">{{ t('student.subscriptions.chips.homework', { n: course.homework_count }) }}</v-chip>
                <v-chip v-if="course.ai_lesson_count" size="x-small" variant="tonal">{{ t('student.subscriptions.chips.ai', { n: course.ai_lesson_count }) }}</v-chip>
                <v-chip size="x-small" variant="tonal">{{ t('student.subscriptions.chips.lessons', { n: course.lesson_count }) }}</v-chip>
              </div>

              <v-btn
                v-if="course.unlocked"
                block
                size="large"
                rounded="lg"
                class="btn-glow"
                :to="ROUTES.STUDENT_COURSE(course.id)"
              >
                <v-icon start>mdi-play-circle</v-icon>
                {{ t('student.subscriptions.cta.continue') }}
              </v-btn>
              <v-btn
                v-else
                block
                size="large"
                rounded="lg"
                class="btn-glow"
                :loading="subscribingId === course.id"
                @click="subscribe(course)"
              >
                <v-icon start>mdi-credit-card</v-icon>
                {{ t('student.subscriptions.cta.subscribe') }}
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <EmptyState
        v-else
        preset="subscriptions"
        :description="t('student.subscriptions.empty')"
      />
    </template>

    <StudentTeacherProfileDialog
      v-model="showTeacherProfile"
      :profile="teacherProfile"
      :loading="loadingTeacherProfile"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import StudentTeacherProfileDialog from '../../components/student/StudentTeacherProfileDialog.vue'
import { fetchSubscriptionsCatalog, subscribeToCourse } from '../../api/subscriptions.js'
import { fetchCourseTeacherProfile } from '../../api/studentCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { formatSyrianPrice } from '../../utils/format.js'
import { useAuth } from '../../composables/useAuth.js'

const { t } = useI18n()
const { session } = useAuth()
const catalog = ref({ courses: [], unlocked_count: 0, available_count: 0, grade: null })
const loading = ref(true)
const loadError = ref('')
const successMsg = ref('')
const subscribingId = ref(null)
const showTeacherProfile = ref(false)
const teacherProfile = ref(null)
const loadingTeacherProfile = ref(false)

const displayName = computed(() => session.value?.name?.split(' ')[0] || t('student.common.defaultStudentName'))
const gradeSubtitle = computed(() =>
  catalog.value.grade ? t('student.subscriptions.header.subtitleWithGrade', { grade: catalog.value.grade }) : t('student.subscriptions.header.subtitleNoGrade'),
)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    catalog.value = await fetchSubscriptionsCatalog()
  } catch (e) {
    loadError.value = getErrorMessage(e, t('student.subscriptions.errors.load'))
  } finally {
    loading.value = false
  }
}

async function subscribe(course) {
  subscribingId.value = course.id
  successMsg.value = ''
  try {
    await subscribeToCourse(course.id, 'card')
    successMsg.value = t('student.subscriptions.success.activated', { subject: course.subject_name })
    await load()
  } catch (e) {
    loadError.value = getErrorMessage(e, t('student.subscriptions.errors.subscribe'))
  } finally {
    subscribingId.value = null
  }
}

async function openTeacherProfile(course) {
  if (!course?.id) return
  showTeacherProfile.value = true
  loadingTeacherProfile.value = true
  teacherProfile.value = null
  try {
    teacherProfile.value = await fetchCourseTeacherProfile(course.id)
  } catch (e) {
    loadError.value = getErrorMessage(e, t('student.subscriptions.errors.loadTeacherProfile'))
    showTeacherProfile.value = false
  } finally {
    loadingTeacherProfile.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.min-width-0 {
  min-width: 0;
}

.teacher-profile-trigger,
.teacher-name-link {
  background: none;
  border: none;
  cursor: pointer;
  text-align: inherit;
  font: inherit;
  color: inherit;
}

.teacher-name-link:hover {
  color: rgb(var(--v-theme-secondary));
  text-decoration: underline;
}
</style>
