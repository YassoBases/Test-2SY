const PAYMENT_RESULT_KEY = 'eduspark_last_payment'

export function setLastPaymentResult(result) {
  try {
    sessionStorage.setItem(PAYMENT_RESULT_KEY, JSON.stringify(result))
  } catch {
    /* ignore quota */
  }
}

export function getLastPaymentResult() {
  try {
    const raw = sessionStorage.getItem(PAYMENT_RESULT_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearLastPaymentResult() {
  sessionStorage.removeItem(PAYMENT_RESULT_KEY)
}
