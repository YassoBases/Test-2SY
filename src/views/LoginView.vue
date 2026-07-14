<template>
  <AuthExperienceShell :footer-link="registerFooterLink">
    <template #brand>
      <EduMindLogo size="auth" />
    </template>

    <div class="auth-experience__intro">
      <h1 class="auth-experience__welcome">{{ roleCopy.welcome }}</h1>
      <p class="auth-experience__context">{{ roleCopy.context }}</p>
      <span class="auth-experience__role-chip">
        <v-icon size="14">{{ roleCopy.icon }}</v-icon>
        {{ roleCopy.label }}
      </span>
    </div>

    <v-form @submit.prevent="handleLogin">
      <v-text-field
        v-model="email"
        :label="t('auth.fields.email')"
        type="email"
        prepend-inner-icon="mdi-email-outline"
        autocomplete="email"
        :error-messages="errors.email"
        class="mb-2"
        @update:model-value="clearError('email')"
      />

      <v-text-field
        v-model="password"
        :label="t('auth.fields.password')"
        :type="showPassword ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock-outline"
        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        autocomplete="current-password"
        :error-messages="errors.password"
        class="mb-2"
        @click:append-inner="showPassword = !showPassword"
        @update:model-value="clearError('password')"
      />

      <div class="text-end mb-4">
        <router-link :to="ROUTES.FORGOT_PASSWORD" class="auth-experience__link text-caption">
          {{ t('auth.login.forgotPassword') }}
        </router-link>
      </div>

      <v-alert
        v-if="role === 'parent'"
        type="info"
        variant="tonal"
        density="compact"
        class="mb-4 rounded-lg"
      >
        {{ t('auth.login.parentAlert') }}
        <router-link :to="parentRegisterLink" class="auth-experience__link ms-1">
          {{ t('auth.login.parentAlertRegister') }}
        </router-link>
      </v-alert>

      <v-alert
        v-if="submitError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4 rounded-lg"
      >
        {{ submitError }}
      </v-alert>

      <v-btn
        type="submit"
        size="large"
        block
        rounded="lg"
        color="secondary"
        variant="flat"
        class="btn-glow mb-3"
        :loading="loading"
      >
        {{ t('auth.login.submit') }}
      </v-btn>

      <p class="text-center text-caption text-medium-emphasis mb-0">
        {{ t('auth.login.termsNotice') }}
      </p>
    </v-form>

    <router-link :to="ROUTES.WELCOME" class="auth-experience__change-role">
      {{ t('auth.login.changeRole', { role: roleCopy.label }) }}
    </router-link>
  </AuthExperienceShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AuthExperienceShell from '../components/auth/AuthExperienceShell.vue'
import EduMindLogo from '../components/auth/EduMindLogo.vue'
import { useAuth } from '../composables/useAuth.js'
import { validateLogin } from '../utils/validate.js'
import { getErrorMessage } from '../api/client.js'
import { clearSession } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'
import { isValidAuthRole, readAuthRole, saveAuthRole } from '../utils/authRole.js'

const ROLE_ICONS = {
  student: 'mdi-account-school-outline',
  parent: 'mdi-account-child-outline',
  teacher: 'mdi-school-outline',
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { login } = useAuth()

const role = ref('student')
const email = ref('student@eduspark.sy')
const password = ref('student123')
const showPassword = ref(false)
const loading = ref(false)
const submitError = ref('')
const errors = reactive({})

const roleKey = computed(() => (isValidAuthRole(role.value) ? role.value : 'student'))

const roleCopy = computed(() => ({
  welcome: t(`auth.roles.${roleKey.value}.welcome`),
  context: t(`auth.roles.${roleKey.value}.context`),
  label: t(`auth.roles.${roleKey.value}.label`),
  icon: ROLE_ICONS[roleKey.value],
}))

const registerFooterLink = computed(() => ({
  text: t('auth.footer.noAccount'),
  label: t('auth.footer.register'),
  to: route.query.entry === 'welcome'
    ? `/register?entry=welcome&role=${role.value}`
    : `/register?role=${role.value}`,
}))

const parentRegisterLink = computed(() =>
  route.query.entry === 'welcome' ? '/register?entry=welcome&role=parent' : '/register?role=parent',
)

onMounted(() => {
  if (route.query.entry === 'welcome') {
    clearSession()
  }

  const fromQuery = route.query.role
  if (isValidAuthRole(fromQuery)) {
    role.value = fromQuery
    saveAuthRole(fromQuery)
    return
  }

  const saved = readAuthRole()
  if (saved) {
    role.value = saved
    return
  }

  if (!route.query.redirect) {
    router.replace(ROUTES.WELCOME)
  }
})

function clearError(field) {
  delete errors[field]
  submitError.value = ''
}

async function handleLogin() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const validation = validateLogin({ email: email.value, password: password.value })
  Object.assign(errors, validation)
  if (Object.keys(validation).length) return

  loading.value = true
  submitError.value = ''
  try {
    await login({
      email: email.value,
      password: password.value,
      name: t(`auth.login.demoNames.${role.value}`),
      role: role.value,
    })
  } catch (err) {
    submitError.value = getErrorMessage(err, t('auth.login.errors.failed'))
  } finally {
    loading.value = false
  }
}
</script>
