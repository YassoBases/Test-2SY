export const AUTH_ROLE_KEY = 'eduspark-auth-role'

export const VALID_AUTH_ROLES = ['student', 'parent', 'teacher']

export const AUTH_ROLE_COPY = {
  student: {
    welcome: 'مرحباً بعودتك',
    context: 'تابع رحلتك التعليمية',
    label: 'طالب',
    icon: 'mdi-account-school-outline',
  },
  parent: {
    welcome: 'مرحباً بك',
    context: 'تابع تقدم أبنائك بسهولة',
    label: 'ولي أمر',
    icon: 'mdi-account-child-outline',
  },
  teacher: {
    welcome: 'مرحباً بعودتك',
    context: 'أدر دروسك وطلابك من مكان واحد',
    label: 'معلم',
    icon: 'mdi-school-outline',
  },
}

export function isValidAuthRole(value) {
  return VALID_AUTH_ROLES.includes(value)
}

export function saveAuthRole(role) {
  try {
    sessionStorage.setItem(AUTH_ROLE_KEY, role)
  } catch {
    /* ignore */
  }
}

export function readAuthRole() {
  try {
    const saved = sessionStorage.getItem(AUTH_ROLE_KEY)
    return isValidAuthRole(saved) ? saved : null
  } catch {
    return null
  }
}
