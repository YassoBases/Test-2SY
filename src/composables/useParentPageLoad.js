import { onActivated, onMounted, watch } from 'vue'
import { parentDebug } from '../utils/parentDebug.js'

/**
 * Load page data once after students are ready, and again when selectedStudentId changes.
 */
export function useParentPageLoad(shell, loadPageData, pageName = 'unknown', { beforeLoad } = {}) {
  async function runLoad(trigger) {
    parentDebug(pageName, 'page-load-start', { trigger, selectedStudentId: shell.selectedStudentId.value })
    beforeLoad?.()
    await loadPageData()
    parentDebug(pageName, 'page-load-finish', { trigger })
  }

  onMounted(async () => {
    parentDebug(pageName, 'page-mounted')
    beforeLoad?.()
    await shell.init()
    if (shell.selectedStudentId.value != null) {
      await runLoad('mount')
    }
  })

  onActivated(async () => {
    parentDebug(pageName, 'page-activated', { selectedStudentId: shell.selectedStudentId.value })
    if (shell.selectedStudentId.value != null) {
      await runLoad('activated')
    }
  })

  watch(
    () => [shell.ready.value, shell.selectedStudentId.value],
    async ([ready, id], prev) => {
      if (!ready || id == null) return
      const prevId = prev?.[1]
      if (prevId === id) return
      await runLoad('student-change')
    },
  )
}
