<template>
  <div class="auth-experience" dir="rtl">
    <WelcomeBackground />

    <header class="auth-experience__toolbar">
      <router-link :to="ROUTES.WELCOME" class="auth-experience__back" :aria-label="t('auth.shell.backAria')">
        <v-icon size="20">mdi-arrow-right</v-icon>
      </router-link>
      <div class="auth-experience__toolbar-actions">
        <LanguageSwitcher />
        <AuthThemePreference compact />
      </div>
    </header>

    <div class="auth-experience__main">
      <div class="auth-experience__card">
        <div class="auth-experience__brand">
          <slot name="brand">
            <EduMindLogo size="auth" />
          </slot>
        </div>
        <slot />
      </div>

      <p v-if="footerLink" class="auth-experience__footer">
        <span>{{ footerLink.text }} </span>
        <router-link :to="footerLink.to" class="auth-experience__link">{{ footerLink.label }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import WelcomeBackground from '../welcome/WelcomeBackground.vue'
import AuthThemePreference from './AuthThemePreference.vue'
import LanguageSwitcher from '../common/LanguageSwitcher.vue'
import EduMindLogo from './EduMindLogo.vue'
import { ROUTES } from '../../constants/app.js'
import '../../assets/styles/auth-experience.css'
import '../../assets/styles/welcome-morning.css'

defineProps({
  footerLink: { type: Object, default: null },
})

const { t } = useI18n()
</script>
