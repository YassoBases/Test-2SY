<template>
  <div class="parent-link-page slide-up-enter-active">
    <PageHeader
      :eyebrow="t('parent.link.eyebrow')"
      eyebrow-icon="mdi-link-variant"
      :title="t('parent.link.title')"
      :subtitle="t('parent.link.subtitle')"
      gradient-title
    />

    <v-alert
      v-if="studentsError"
      type="warning"
      variant="tonal"
      class="mb-5 rounded-lg"
    >
      {{ studentsError }}
    </v-alert>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <ParentLinkStudentForm
          :linking="linking"
          :link-error="linkError"
          :link-success="linkSuccess"
          :has-students="hasStudents"
          @submit="onLink"
          @clear-error="linkError = ''"
          @clear-success="linkSuccess = ''"
        />
      </v-col>
    </v-row>

    <section v-if="hasStudents" class="mt-8">
      <h3 class="text-h6 font-weight-bold mb-4 d-flex align-center gap-2">
        <v-icon color="primary">mdi-account-group</v-icon>
        {{ t('parent.link.linkedStudents') }}
      </h3>
      <v-row>
        <v-col
          v-for="student in students"
          :key="student.id"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card class="glass-card pa-4" variant="flat">
            <div class="d-flex align-center gap-3">
              <v-avatar class="eduspark-gradient" size="44">
                <span class="text-body-2 font-weight-bold text-white">
                  {{ student.name?.charAt(0) }}
                </span>
              </v-avatar>
              <div class="text-truncate">
                <div class="font-weight-bold text-truncate">{{ student.name }}</div>
                <div class="text-caption text-medium-emphasis text-truncate">
                  {{ student.email }}
                </div>
              </div>
            </div>
            <v-btn
              class="mt-4"
              block
              variant="tonal"
              color="primary"
              size="small"
              @click="goToDashboard(student.id)"
            >
              {{ t('parent.link.viewMonitoring') }}
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import ParentLinkStudentForm from '../../components/parent/ParentLinkStudentForm.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { ROUTES } from '../../constants/app.js'

const { t } = useI18n()
const router = useRouter()

const {
  students,
  hasStudents,
  studentsError,
  linking,
  linkError,
  linkSuccess,
  selectStudent,
  linkStudent,
  reloadStudents,
} = useParentShell()

onMounted(() => reloadStudents())

async function onLink(code) {
  const ok = await linkStudent(code)
  if (ok && students.value.length === 1) {
    router.push(ROUTES.PARENT_DASHBOARD)
  }
}

function goToDashboard(studentId) {
  selectStudent(studentId)
  router.push(ROUTES.PARENT_DASHBOARD)
}
</script>

<style scoped>
.parent-link-page {
  max-width: 960px;
  margin-inline: auto;
}
</style>
