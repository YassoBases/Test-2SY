<template>
  <div class="role-paths" :class="{ 'role-paths--centered': centered }">
    <p v-if="centered" class="role-paths__label welcome-enter welcome-enter--roles-label">
      {{ t('auth.welcome.rolePathsLabel') }}
    </p>
    <div class="role-paths__grid">
      <button
        v-for="(role, i) in roles"
        :key="role.key"
        type="button"
        class="role-path welcome-enter welcome-enter--role"
        :class="{
          'role-path--active': selectedRole === role.key,
          [`role-path--${role.key}`]: true,
        }"
        :style="{ animationDelay: `${1020 + i * 120}ms` }"
        :aria-pressed="selectedRole === role.key"
        @click="$emit('select', role.key)"
      >
        <span v-if="selectedRole === role.key" class="role-path__check" aria-hidden="true">
          <v-icon size="14" color="primary">mdi-check-circle</v-icon>
        </span>
        <span class="role-path__icon-wrap" :class="`role-path__icon-wrap--${role.key}`">
          <v-icon :size="role.iconSize" :color="role.iconColor">{{ role.icon }}</v-icon>
        </span>
        <span class="role-path__title">{{ role.title }}</span>
        <span class="role-path__tagline">{{ role.tagline }}</span>
        <span class="role-path__detail">{{ role.detail }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  centered: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
  selectedRole: { type: String, default: null },
})

defineEmits(['select'])

const { t } = useI18n()

const ROLE_META = [
  { key: 'student', icon: 'mdi-account-school-outline', iconColor: 'secondary', iconSize: 24 },
  { key: 'parent', icon: 'mdi-account-child-outline', iconColor: 'warning', iconSize: 22 },
  { key: 'teacher', icon: 'mdi-school-outline', iconColor: 'primary', iconSize: 22 },
]

const roles = computed(() =>
  ROLE_META.map((meta) => ({
    ...meta,
    title: t(`auth.welcome.roles.${meta.key}.title`),
    tagline: t(`auth.welcome.roles.${meta.key}.tagline`),
    detail: t(`auth.welcome.roles.${meta.key}.detail`),
  })),
)
</script>
