<template>
  <div class="welcome-page" dir="rtl">
    <WelcomeBackground />

    <header class="welcome-page__toolbar">
      <div class="welcome-page__toolbar-actions">
        <LanguageSwitcher />
        <AuthThemePreference compact />
      </div>
    </header>

    <div class="welcome-shell">
      <header class="welcome-hero">
        <div class="welcome-enter welcome-enter--logo">
          <WelcomeBrandLockup centered />
        </div>

        <h1 class="welcome-headline welcome-enter welcome-enter--headline">
          {{ t('auth.welcome.headline') }}
        </h1>

        <p class="hero-desc welcome-enter welcome-enter--desc">
          {{ t('auth.welcome.description') }}
        </p>

        <WelcomeValueChips />
      </header>

      <div class="welcome-cards">
        <WelcomeFeatureCards
          compact
          centered
          :selected-role="selectedRole"
          :navigating="isNavigating"
          @select="onRoleSelect"
        />
      </div>

      <footer class="welcome-footer welcome-enter welcome-enter--footer">
        <WelcomeTrustSection />
      </footer>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import WelcomeBackground from '../components/welcome/WelcomeBackground.vue'
import WelcomeBrandLockup from '../components/welcome/WelcomeBrandLockup.vue'
import WelcomeValueChips from '../components/welcome/WelcomeValueChips.vue'
import WelcomeFeatureCards from '../components/welcome/WelcomeFeatureCards.vue'
import WelcomeTrustSection from '../components/welcome/WelcomeTrustSection.vue'
import AuthThemePreference from '../components/auth/AuthThemePreference.vue'
import LanguageSwitcher from '../components/common/LanguageSwitcher.vue'
import { ROUTES } from '../constants/app.js'
import { saveAuthRole } from '../utils/authRole.js'
import '../assets/styles/welcome-landing.css'
import '../assets/styles/welcome-landing-3.css'
import '../assets/styles/auth-experience.css'
import '../assets/styles/welcome-morning.css'

const { t } = useI18n()
const router = useRouter()
const selectedRole = ref(null)
const isNavigating = ref(false)

function onRoleSelect(role) {
  if (isNavigating.value) return
  selectedRole.value = role
  isNavigating.value = true
  saveAuthRole(role)
  window.setTimeout(() => {
    router.push({ path: ROUTES.LOGIN, query: { entry: 'welcome', role } })
  }, 520)
}

onMounted(() => {
  document.documentElement.classList.add('welcome-no-scroll')
  document.body.classList.add('welcome-no-scroll')
})

onUnmounted(() => {
  document.documentElement.classList.remove('welcome-no-scroll')
  document.body.classList.remove('welcome-no-scroll')
})
</script>

<style scoped>
.welcome-page {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  height: 100dvh;
  max-height: 100dvh;
  overflow: hidden;
}

.welcome-page__toolbar {
  position: absolute;
  top: clamp(0.75rem, 2.2vh, 1.1rem);
  inset-inline-end: clamp(0.85rem, 3vw, 1.5rem);
  z-index: 3;
}

.welcome-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
  flex-shrink: 0;
}

.welcome-headline {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.12rem, 2.6vh, 1.42rem);
  font-weight: 800;
  line-height: 1.28;
  color: var(--em-text);
  letter-spacing: -0.02em;
}

.hero-desc {
  margin: 0 auto;
  font-size: clamp(0.8rem, 1.55vh, 0.9rem);
  line-height: 1.6;
  color: var(--em-text-muted);
}

.welcome-cards,
.welcome-footer {
  width: 100%;
  flex-shrink: 0;
}

@media (max-height: 720px) {
  .welcome-headline {
    font-size: 1.05rem;
  }

  .hero-desc {
    font-size: 0.74rem;
    line-height: 1.5;
  }
}
</style>

<style>
html.welcome-no-scroll,
body.welcome-no-scroll {
  overflow: hidden !important;
  height: 100%;
  max-height: 100dvh;
}

.eduspark-app:has(.welcome-page) {
  min-height: 100dvh;
  max-height: 100dvh;
  overflow: hidden;
}

.eduspark-app:has(.welcome-page) .page-content {
  height: 100dvh;
  max-height: 100dvh;
  overflow: hidden;
}
</style>
