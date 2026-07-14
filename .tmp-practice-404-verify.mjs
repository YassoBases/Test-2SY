import { chromium, request as playwrightRequest } from 'playwright'

const BASE = 'http://localhost:5174'
const API = 'http://127.0.0.1:8000'
const EMAIL = 'qa.listening.student-e@eduspark-test.dev'
const PASSWORD = 'TestOnly123!'

async function login() {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.post('/api/auth/login', { data: { email: EMAIL, password: PASSWORD } })
  const data = await res.json()
  await ctx.dispose()
  return {
    ...data.user,
    accessToken: data.access_token,
    refreshToken: data.refresh_token || null,
    loggedInAt: new Date().toISOString(),
    onboardingComplete: true,
  }
}

async function main() {
  const session = await login()
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ locale: 'en-US' })
  await context.addInitScript((s) => {
    localStorage.setItem('eduspark_session', JSON.stringify(s))
    localStorage.setItem('eduspark-locale', 'en')
  }, session)
  const page = await context.newPage()
  const captured = []
  page.on('response', async (res) => {
    const url = res.url()
    if (url.includes('/api/student/languages/listening/next')) {
      let body = ''
      try {
        body = await res.text()
      } catch {
        body = '<unreadable>'
      }
      captured.push({
        method: res.request().method(),
        url,
        status: res.status(),
        body: body.slice(0, 500),
      })
    }
  })

  await page.goto(`${BASE}/student/languages/listening?tab=practice`, {
    waitUntil: 'networkidle',
    timeout: 120000,
  })
  await page.waitForTimeout(1500)
  const start = page.getByRole('button', { name: /start|practice|play/i }).first()
  if (await start.isVisible()) {
    await start.click()
    await page.waitForTimeout(8000)
  }

  console.log(JSON.stringify(captured, null, 2))
  await browser.close()
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
