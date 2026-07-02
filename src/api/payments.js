import { api } from './client.js'

export async function fetchCheckout() {
  const { data } = await api.get('/student/payments/checkout')
  return data
}

export async function demoCheckout(method) {
  const { data } = await api.post('/student/payments/demo-checkout', { method })
  return data
}
