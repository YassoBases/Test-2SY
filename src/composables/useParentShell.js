import { computed, inject, provide, ref } from 'vue'
import { useParentStudents } from './useParentStudents.js'
import { parentDebug } from '../utils/parentDebug.js'

export const PARENT_SHELL_KEY = Symbol('parentShell')

function createParentShellState() {
  const studentsApi = useParentStudents()
  const ready = ref(false)
  let initPromise = null

  async function init() {
    if (ready.value) return
    parentDebug('shell', 'init-start')
    if (!initPromise) {
      initPromise = studentsApi.loadStudents().then(() => {
        ready.value = true
        parentDebug('shell', 'init-success', { selectedStudentId: studentsApi.selectedStudentId.value })
      })
    }
    await initPromise
  }

  async function reloadStudents() {
    await studentsApi.loadStudents()
    ready.value = true
  }

  const studentContext = computed(() => {
    const s = studentsApi.selectedStudent.value
    if (!s) return null
    return {
      id: s.id,
      name: s.name,
      grade: s.grade ?? null,
      grade_label: s.grade_label ?? null,
    }
  })

  return {
    ...studentsApi,
    ready,
    init,
    reloadStudents,
    studentContext,
  }
}

/** Call once from ParentLayout — shared across all parent pages. */
export function provideParentShell() {
  const shell = createParentShellState()
  provide(PARENT_SHELL_KEY, shell)
  return shell
}

/** Inject the layout-provided shell (students loaded once, reused on navigation). */
export function useParentShell() {
  const shell = inject(PARENT_SHELL_KEY, null)
  if (!shell) {
    throw new Error('useParentShell() must be used within ParentLayout')
  }
  return shell
}
