<template>
  <div class="auth-theme" :class="{ 'auth-theme--compact': compact }" role="group" :aria-label="t('common.theme.aria')">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      class="auth-theme__btn"
      :class="{ 'auth-theme__btn--active': preference === opt.value }"
      :aria-pressed="preference === opt.value"
      @click="setPreference(opt.value)"
    >
      <v-icon size="16">{{ opt.icon }}</v-icon>
      <span>{{ opt.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeMode } from '../../composables/useThemeMode.js'

defineProps({
  compact: { type: Boolean, default: false },
})

const { t } = useI18n()
const { preference, setPreference } = useThemeMode()

const options = computed(() => [
  { value: 'system', label: t('common.theme.system'), icon: 'mdi-laptop' },
  { value: 'light', label: t('common.theme.light'), icon: 'mdi-white-balance-sunny' },
  { value: 'dark', label: t('common.theme.dark'), icon: 'mdi-weather-night' },
])
</script>

<style scoped>
.auth-theme {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0.2rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(8, 12, 24, 0.45);
  backdrop-filter: blur(10px);
}

[data-theme='morning'] .auth-theme {
  border-color: rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.72);
}

.auth-theme__btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.65rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: rgba(232, 236, 255, 0.55);
  font-family: inherit;
  font-size: 0.68rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

[data-theme='morning'] .auth-theme__btn {
  color: rgba(15, 23, 42, 0.55);
}

.auth-theme__btn--active {
  color: var(--em-cyan, rgb(var(--v-theme-secondary)));
  background: rgba(34, 211, 238, 0.12);
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.12);
}

[data-theme='morning'] .auth-theme__btn--active {
  color: rgb(var(--v-theme-primary));
  background: rgba(99, 102, 241, 0.1);
  box-shadow: none;
}

.auth-theme--compact .auth-theme__btn span {
  display: none;
}

.auth-theme--compact .auth-theme__btn {
  padding: 0.4rem;
}
</style>
