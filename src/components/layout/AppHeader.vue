<template>
  <v-app-bar flat height="64" class="app-header px-2 px-md-4">
    <v-app-bar-nav-icon
      class="d-md-none app-header__menu"
      @click="$emit('toggle-drawer')"
    />

    <div class="app-header__title-block min-width-0">
      <p v-if="breadcrumbs" class="app-header__crumb text-truncate">{{ breadcrumbs }}</p>
      <v-toolbar-title class="app-header__title text-truncate">
        {{ title }}
      </v-toolbar-title>
    </div>

    <v-spacer />

    <div class="app-header__actions d-flex align-center gap-1">
      <LanguageSwitcher />
      <ThemeToggle />
      <NotificationBell />

      <template v-if="role === 'teacher'">
        <v-btn
          class="btn-glow d-none d-sm-flex"
          prepend-icon="mdi-school-outline"
          size="small"
          to="/teacher/grades"
        >
          {{ t('common.classes') }}
        </v-btn>
        <v-btn
          class="d-sm-none"
          icon
          variant="tonal"
          color="primary"
          to="/teacher/grades"
        >
          <v-icon>mdi-school-outline</v-icon>
        </v-btn>
      </template>

      <v-menu location="bottom end" :close-on-content-click="true">
        <template #activator="{ props: menuProps }">
          <button type="button" class="app-header__profile em-press" v-bind="menuProps">
            <TeacherAvatar
              v-if="role === 'teacher'"
              :name="headerDisplayName"
              :image-url="teacherProfile.image_url"
              :size="36"
            />
            <v-avatar v-else size="36" class="app-header__avatar">
              <span v-if="userInitial" class="text-body-2 font-weight-bold">
                {{ userInitial }}
              </span>
              <v-icon v-else size="18">mdi-account</v-icon>
            </v-avatar>
            <span class="app-header__name d-none d-sm-inline text-truncate">
              {{ headerDisplayName || t('common.header.accountFallback') }}
            </span>
            <v-icon size="18" class="app-header__chevron d-none d-sm-inline">mdi-chevron-down</v-icon>
          </button>
        </template>
        <v-list class="app-header__menu glass-card glass-card--solid" density="compact">
          <v-list-item
            v-if="role === 'student'"
            prepend-icon="mdi-account-circle-outline"
            :title="t('common.profile')"
            :subtitle="t('common.header.studentProfileSubtitle')"
            to="/student/profile"
          />
          <v-list-item
            v-if="role === 'teacher'"
            prepend-icon="mdi-account-circle-outline"
            :title="t('common.profile')"
            :subtitle="t('common.header.teacherProfileSubtitle')"
            :to="ROUTES.TEACHER_PROFILE"
          />
          <v-list-item
            prepend-icon="mdi-shield-lock-outline"
            :title="t('common.securityDevices')"
            :to="settingsTo"
          />
          <v-divider class="my-1" />
          <v-list-item
            prepend-icon="mdi-logout"
            :title="t('common.logout')"
            base-color="error"
            @click="logout"
          />
        </v-list>
      </v-menu>
    </div>
  </v-app-bar>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import NotificationBell from './NotificationBell.vue'
import TeacherAvatar from '../onboarding/TeacherAvatar.vue'
import ThemeToggle from '../ui/ThemeToggle.vue'
import LanguageSwitcher from '../common/LanguageSwitcher.vue'
import { useAuth } from '../../composables/useAuth.js'
import { useTeacherProfile } from '../../composables/useTeacherProfile.js'
import { ROUTES, settingsRouteForRole } from '../../constants/app.js'

const props = defineProps({
  title: { type: String, default: '' },
  breadcrumbs: { type: String, default: '' },
  role: { type: String, default: 'teacher' },
})

defineEmits(['toggle-drawer'])

const { t } = useI18n()
const { user, logout } = useAuth()
const { teacherProfile, ensureTeacherProfile } = useTeacherProfile()

const settingsTo = computed(() => settingsRouteForRole(props.role))

const userInitial = computed(() => user.value?.name?.charAt(0) ?? '')
const headerDisplayName = computed(
  () => teacherProfile.value.full_name || user.value?.name || '',
)

onMounted(() => {
  if (props.role === 'teacher') ensureTeacherProfile()
})
</script>

<style scoped>
.app-header {
  background: var(--em-header-bg) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--em-border-subtle);
}

.app-header__title-block {
  max-width: min(420px, 55vw);
}

.app-header__crumb {
  margin: 0;
  font-size: var(--em-text-caption);
  color: var(--em-text-subtle);
  line-height: 1.2;
}

.app-header__title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--em-text);
  padding-inline-start: 0;
}

.app-header__actions {
  flex-shrink: 0;
}

.app-header__profile {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px 6px 6px;
  margin-inline-start: 4px;
  border: 1px solid var(--em-border);
  border-radius: var(--em-radius-sm);
  background: var(--em-surface);
  cursor: pointer;
  transition:
    border-color var(--em-duration-fast) var(--em-ease-out),
    box-shadow var(--em-duration-fast) var(--em-ease-out);
}

.app-header__profile:hover {
  border-color: var(--em-border-bright);
  box-shadow: var(--em-shadow-sm);
}

.app-header__avatar {
  background: linear-gradient(135deg, var(--em-primary-hover), var(--em-blue-soft));
  color: #fff;
}

.app-header__name {
  max-width: 140px;
  font-size: var(--em-text-sm);
  font-weight: 600;
  color: var(--em-text);
}

.app-header__chevron {
  color: var(--em-text-muted);
}

.app-header__menu {
  min-width: 240px;
  border-radius: var(--em-radius-md) !important;
}

.min-width-0 {
  min-width: 0;
}
</style>
