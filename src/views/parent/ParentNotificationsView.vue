<template>
  <ParentPortalShell
    :title="t('parent.notifications.title')"
    :subtitle="t('parent.notifications.subtitle')"
    :students="students"
    :selected-student-id="selectedStudentId"
    :student-context="studentContext"
    :has-students="hasStudents"
    :loading-students="loadingStudents"
    :students-error="studentsError"
    :linking="linking"
    :link-error="linkError"
    :link-success="linkSuccess"
    :loading="notificationsLoading"
    :load-error="notificationsLoadError"
    @select-student="selectStudent"
    @link="linkStudent"
    @clear-students-error="studentsError = ''"
    @clear-link-error="linkError = ''"
    @clear-link-success="linkSuccess = ''"
    @clear-load-error="notificationsLoadError = ''"
  >
    <ParentNotificationsSection
      :items="notificationItems"
      :unread-count="notificationUnreadCount"
      :settings="notificationSettings"
      :loading="notificationsLoading"
      :settings-loading="notificationSettingsLoading"
      :saving-settings="notificationSavingSettings"
      :load-error="notificationsLoadError"
      :settings-error="notificationSettingsError"
      @mark-read="markNotificationRead"
      @save-settings="saveNotificationSettings"
    />
  </ParentPortalShell>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import ParentPortalShell from '../../components/parent/portal/ParentPortalShell.vue'
import ParentNotificationsSection from '../../components/parent/ParentNotificationsSection.vue'
import { useParentShell } from '../../composables/useParentShell.js'
import { useParentNotifications } from '../../composables/useParentNotifications.js'
import { useParentPageLoad } from '../../composables/useParentPageLoad.js'

const { t } = useI18n()

const shell = useParentShell()
const {
  students,
  selectedStudentId,
  studentContext,
  hasStudents,
  loadingStudents,
  studentsError,
  linking,
  linkError,
  linkSuccess,
  selectStudent,
  linkStudent,
} = shell

const notifications = useParentNotifications(shell.selectedStudentId)
const {
  items: notificationItems,
  unreadCount: notificationUnreadCount,
  settings: notificationSettings,
  loading: notificationsLoading,
  settingsLoading: notificationSettingsLoading,
  savingSettings: notificationSavingSettings,
  loadError: notificationsLoadError,
  settingsError: notificationSettingsError,
  markRead: markNotificationRead,
  saveSettings: saveNotificationSettings,
  loadAll,
} = notifications

useParentPageLoad(shell, loadAll, 'notifications')
</script>
