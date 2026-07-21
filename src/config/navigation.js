export const teacherNavItems = [
  { titleKey: 'dashboard.teacher.nav.home', icon: 'mdi-view-dashboard', to: '/teacher/dashboard' },
  { titleKey: 'dashboard.teacher.nav.grades', icon: 'mdi-school-outline', to: '/teacher/grades', matchChildren: true },
  { titleKey: 'dashboard.teacher.nav.messages', icon: 'mdi-message-text-outline', to: '/teacher/messages' },
  { titleKey: 'dashboard.teacher.nav.quizzes', icon: 'mdi-clipboard-text-outline', to: '/teacher/quizzes', matchChildren: true },
  { titleKey: 'dashboard.teacher.nav.analytics', icon: 'mdi-chart-line', to: '/teacher/analytics' },
  { titleKey: 'dashboard.teacher.nav.profile', icon: 'mdi-account-cog', to: '/teacher/profile' },
  { titleKey: 'dashboard.teacher.nav.settings', icon: 'mdi-shield-account', to: '/teacher/settings' },
]

export const studentNavItems = [
  { titleKey: 'dashboard.student.nav.englishJourney', icon: 'mdi-earth', to: '/student/english-journey', premium: true, matchChildren: true, section: 'learning' },
  { titleKey: 'dashboard.student.nav.journey', icon: 'mdi-map-marker-path', to: '/student/dashboard#courses', section: 'learning' },
  { titleKey: 'dashboard.student.nav.messages', icon: 'mdi-message-text-outline', to: '/student/messages', section: 'learning' },
  { titleKey: 'dashboard.student.nav.languages', icon: 'mdi-translate', to: '/student/languages', premium: true, matchChildren: true, section: 'learning' },
  { titleKey: 'dashboard.student.nav.subscriptions', icon: 'mdi-credit-card-outline', to: '/student/subscriptions', section: 'planning' },
  { titleKey: 'dashboard.student.nav.routine', icon: 'mdi-calendar-clock', to: '/student/routine', section: 'planning' },
  { titleKey: 'dashboard.student.nav.planner', icon: 'mdi-brain', to: '/student/planner', section: 'planning' },
  { titleKey: 'dashboard.student.nav.achievements', icon: 'mdi-trophy-outline', to: '/student/achievements', section: 'account' },
  { titleKey: 'dashboard.student.nav.profile', icon: 'mdi-account-cog', to: '/student/profile', section: 'account' },
  { titleKey: 'dashboard.student.nav.settings', icon: 'mdi-shield-account', to: '/student/settings', section: 'account' },
]

export const parentNavItems = [
  { titleKey: 'dashboard.parent.nav.dashboard', icon: 'mdi-view-dashboard-outline', to: '/parent/dashboard' },
  { titleKey: 'dashboard.parent.nav.performance', icon: 'mdi-school-outline', to: '/parent/student-performance' },
  { titleKey: 'dashboard.parent.nav.attendance', icon: 'mdi-clock-check-outline', to: '/parent/student-attendance' },
  { titleKey: 'dashboard.parent.nav.lessons', icon: 'mdi-book-check-outline', to: '/parent/student-lessons' },
  { titleKey: 'dashboard.parent.nav.subjectsTeachers', icon: 'mdi-book-education-outline', to: '/parent/subjects-teachers' },
  { titleKey: 'dashboard.parent.nav.planner', icon: 'mdi-calendar-star', to: '/parent/student-planner' },
  { titleKey: 'dashboard.parent.nav.notifications', icon: 'mdi-bell-alert-outline', to: '/parent/student-notifications' },
  { titleKey: 'dashboard.parent.nav.insights', icon: 'mdi-creation', to: '/parent/student-insights' },
  { titleKey: 'dashboard.parent.nav.reports', icon: 'mdi-file-chart-outline', to: '/parent/student-reports' },
  { titleKey: 'dashboard.parent.nav.messages', icon: 'mdi-message-text-outline', to: '/parent/messages' },
  { titleKey: 'dashboard.parent.nav.settings', icon: 'mdi-shield-account', to: '/parent/settings' },
]
