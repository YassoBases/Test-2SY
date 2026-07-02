import { reactive } from 'vue'

export const toastState = reactive({
  show: false,
  text: '',
  type: 'success',
  timeout: 4000,
})

let hideTimer = null

export function useToast() {
  function showToast(text, type = 'success', timeout = 4000) {
    toastState.text = text
    toastState.type = type
    toastState.timeout = timeout
    toastState.show = true
    if (hideTimer) clearTimeout(hideTimer)
    hideTimer = setTimeout(() => {
      toastState.show = false
    }, timeout)
  }

  return {
    toastState,
    showToast,
    showSuccess: (text) => showToast(text, 'success'),
    showError: (text) => showToast(text, 'error', 6000),
    showInfo: (text) => showToast(text, 'info'),
    showWarning: (text) => showToast(text, 'warning'),
  }
}
