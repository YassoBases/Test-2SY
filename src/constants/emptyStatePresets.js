/** Standard empty-state copy + icons for platform lists. Keys resolve via i18n in AppEmptyState. */
export const EMPTY_STATE_PRESETS = {
  messages: {
    icon: 'mdi-message-text-outline',
    titleKey: 'common.emptyState.messages.title',
    descriptionKey: 'common.emptyState.messages.description',
    actionIcon: 'mdi-message-plus',
  },
  lessons: {
    icon: 'mdi-book-open-page-variant-outline',
    titleKey: 'common.emptyState.lessons.title',
    descriptionKey: 'common.emptyState.lessons.description',
    actionLabelKey: 'common.emptyState.lessons.actionLabel',
    actionTo: '/teacher/grades',
    actionIcon: 'mdi-cloud-upload',
  },
  quizzes: {
    icon: 'mdi-clipboard-text-outline',
    titleKey: 'common.emptyState.quizzes.title',
    descriptionKey: 'common.emptyState.quizzes.description',
    actionLabelKey: 'common.emptyState.quizzes.actionLabel',
    actionTo: '/teacher/quizzes',
    actionIcon: 'mdi-plus',
  },
  students: {
    icon: 'mdi-account-group-outline',
    titleKey: 'common.emptyState.students.title',
    descriptionKey: 'common.emptyState.students.description',
  },
  studentsFiltered: {
    icon: 'mdi-account-search-outline',
    titleKey: 'common.emptyState.studentsFiltered.title',
    descriptionKey: 'common.emptyState.studentsFiltered.description',
  },
  subscriptions: {
    icon: 'mdi-credit-card-off-outline',
    titleKey: 'common.emptyState.subscriptions.title',
    descriptionKey: 'common.emptyState.subscriptions.description',
    actionLabelKey: 'common.emptyState.subscriptions.actionLabel',
    actionTo: '/student/dashboard#courses',
    actionIcon: 'mdi-book-education',
  },
  notifications: {
    icon: 'mdi-bell-off-outline',
    titleKey: 'common.emptyState.notifications.title',
    descriptionKey: 'common.emptyState.notifications.description',
  },
  courses: {
    icon: 'mdi-school-outline',
    titleKey: 'common.emptyState.courses.title',
    descriptionKey: 'common.emptyState.courses.description',
  },
  generic: {
    icon: 'mdi-folder-open-outline',
    titleKey: 'common.emptyState.generic.title',
    descriptionKey: 'common.emptyState.generic.description',
  },
}

export function emptyStatePreset(key) {
  return EMPTY_STATE_PRESETS[key] || EMPTY_STATE_PRESETS.generic
}
