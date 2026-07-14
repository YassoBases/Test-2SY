import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { i18n } from './i18n/index.js'
import { installActivityTracking } from './composables/useActivityTracking.js'
import { initThemeMode } from './composables/useThemeMode.js'
import './assets/styles/tokens.css'
import './assets/styles/main.css'
import './assets/styles/design-system.css'
import './assets/styles/motion.css'
import './assets/styles/sidebar.css'
import './assets/styles/sidebar-nav.css'
import './assets/styles/day-mode.css'
import './assets/styles/student-experience.css'
import './assets/styles/teacher-experience.css'
import './assets/styles/teacher-typography.css'
import './assets/styles/teacher-design-system.css'
import './assets/styles/teacher-form-surface.css'
import './assets/styles/ui-6.4-course-messages.css'
import './assets/styles/eduspark-input-surface.css'

initThemeMode()
installActivityTracking(router)

createApp(App).use(i18n).use(router).use(vuetify).mount('#app')
