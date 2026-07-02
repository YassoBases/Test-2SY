<template>
  <div class="slide-up-enter-active">
    <PageHeader
      :eyebrow="t('settings.account.eyebrow')"
      :title="t('settings.account.title')"
      :subtitle="settingsSubtitle"
    />

    <AccountSecuritySection class="mb-6" />

    <SecurityDevicesSection />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import SecurityDevicesSection from '../../components/settings/SecurityDevicesSection.vue'
import AccountSecuritySection from '../../components/profile/AccountSecuritySection.vue'
import { getSession } from '../../utils/session.js'

const props = defineProps({
  roleLabel: { type: String, default: '' },
})

const { t } = useI18n()

const settingsSubtitle = computed(() => {
  const role = props.roleLabel || getSession()?.role
  const roleKey = role && ['student', 'teacher', 'parent', 'admin'].includes(role) ? role : null
  const label = roleKey ? t(`settings.roles.${roleKey}`) : ''
  return label
    ? t('settings.account.subtitleWithRole', { role: label })
    : t('settings.account.subtitleDefault')
})
</script>
