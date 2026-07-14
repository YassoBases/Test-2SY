import { chromium, request as playwrightRequest } from 'playwright'

const BASE = 'http://localhost:5173'
const API = 'http://127.0.0.1:8000'
const CANDIDATES = [
  { email: 'test.student@example.com', password: 'changeme' },
  { email: 'student@eduspark.sy', password: 'student123' },
  { email: 'test.auth.student@eduspark-test.dev', password: 'TestOnly123!' },
]
const I18N_RE = /student\.languages?\./
const failures = []
const network404 = []
const consoleErrors = []
const apiCalls = []

function fail(msg) {
  failures.push(msg)
  console.error('FAIL:', msg)
}

async function authenticate() {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  let lastErr = ''
  for (const { email, password } of CANDIDATES) {
    const res = await ctx.post('/api/auth/login', { data: { email, password } })
    if (!res.ok()) {
      lastErr = `${email}: ${res.status()}`
      continue
    }
    const data = await res.json()
    if (!data.access_token || !data.user) {
      lastErr = `${email}: missing token`
      continue
    }
    await ctx.dispose()
    const u = data.user
    return {
      ...u,
      email: u.email,
      name: u.name || 'Student',
      role: u.role || 'student',
      accessToken: data.access_token,
      refreshToken: data.refresh_token || null,
      sessionId: data.session_id || null,
      loggedInAt: new Date().toISOString(),
      onboardingComplete: u.onboarding_complete ?? u.onboardingComplete ?? true,
    }
  }
  await ctx.dispose()
  throw new Error(`Login API failed for all candidates. Last: ${lastErr}`)
}

async function main() {
  const session = await authenticate()
  console.log('AUTH AS', session.email)

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ locale: 'en-US' })
  await context.addInitScript((s) => {
    localStorage.setItem('eduspark_session', JSON.stringify(s))
    localStorage.setItem('eduspark-locale', 'en')
  }, session)

  const page = await context.newPage()
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => consoleErrors.push(String(err)))
  page.on('response', (res) => {
    const url = res.url()
    if (url.includes('/api/')) {
      apiCalls.push({ url, status: res.status(), method: res.request().method() })
      if (res.status() === 404) network404.push(`${res.request().method()} ${url}`)
    }
  })

  const bodyText = async () => page.locator('body').innerText()

  await page.goto(`${BASE}/student/languages/listening`, { waitUntil: 'networkidle', timeout: 180000 })
  await page.waitForTimeout(3000)

  const currentUrl = page.url()
  const snippet = (await bodyText()).slice(0, 400).replace(/\s+/g, ' ')
  console.log('URL:', currentUrl)
  console.log('SNIPPET:', snippet)

  if (currentUrl.includes('/login')) fail('Redirected to login — session not accepted')
  if (currentUrl.includes('/onboarding') || currentUrl.includes('/subscribe')) {
    fail(`Blocked from listening page: ${currentUrl}`)
  }

  if (I18N_RE.test(await bodyText())) fail('Raw i18n keys visible on Journey tab')
  if (network404.length) fail(`404 requests: ${network404.join('; ')}`)

  const tab = (name) => page.locator('.v-tab').filter({ hasText: new RegExp(name, 'i') }).first()

  if (!(await tab('journey').isVisible().catch(() => false))) {
    fail(`Journey tab did not load at ${currentUrl}`)
  }

  if (!(await page.getByText(/listening goal/i).first().isVisible().catch(() => false))) {
    fail('Goal selector did not load')
  }

  if (!apiCalls.some((c) => c.url.includes('/learner/memory') && c.method === 'GET' && c.status === 200)) {
    fail('Learner memory did not load (no successful GET)')
  }

  await tab('practice').click()
  await page.waitForTimeout(2000)
  if (I18N_RE.test(await bodyText())) fail('Raw i18n keys on Practice tab')

  const startBtn = page.getByRole('button', { name: /start listening/i }).first()
  if (!(await startBtn.isVisible().catch(() => false))) fail('Practice tab did not load')
  await startBtn.click()
  await page.waitForTimeout(15000)

  const submitBtn = page.getByRole('button', { name: /submit answers/i })
  if (!(await submitBtn.isVisible({ timeout: 180000 }).catch(() => false))) {
    fail('Listening lesson did not start')
  } else {
    const radios = page.locator('input[type="radio"]')
    const count = await radios.count()
    const seen = new Set()
    for (let i = 0; i < count; i++) {
      const name = await radios.nth(i).getAttribute('name')
      if (name && !seen.has(name)) {
        seen.add(name)
        await radios.nth(i).check({ force: true })
      }
    }
    const statusBefore = apiCalls.filter((c) => c.url.includes('promotion-test/status')).length
    await submitBtn.click()
    await page.waitForTimeout(10000)
    const statusAfter = apiCalls.filter((c) => c.url.includes('promotion-test/status')).length
    if (statusAfter <= statusBefore) fail('Journey did not refresh after submit')
    if (!(await page.getByText(/nice work|good effort|retry|next clip|well done/i).first().isVisible().catch(() => false))) {
      fail('Submit did not show lesson result')
    }
  }

  await tab('promotion').click()
  await page.waitForTimeout(2500)
  if (I18N_RE.test(await bodyText())) fail('Raw i18n keys on Promotion tab')
  if (!(await page.getByText(/promotion|almost there|unlocked|keep practising/i).first().isVisible().catch(() => false))) {
    fail('Promotion tab did not load')
  }

  await tab('journey').click()
  await page.waitForTimeout(1000)
  const chip = page.locator('.v-chip').filter({ hasText: /travel|ielts|business|daily life/i }).first()
  if (!(await chip.isVisible().catch(() => false))) {
    fail('Could not find goal chip')
  } else {
    const putsBefore = apiCalls.filter((c) => c.url.includes('/learner/memory') && c.method === 'PUT').length
    await chip.click()
    await page.waitForTimeout(3000)
    const putsAfter = apiCalls.filter((c) => c.url.includes('/learner/memory') && c.method === 'PUT').length
    if (putsAfter <= putsBefore) fail('Switching goals did not update learner memory')
  }

  const filteredConsole = consoleErrors.filter(
    (e) => !e.includes('favicon') && !e.includes('404') && !e.includes('Failed to load resource'),
  )
  if (filteredConsole.length) fail(`Console errors: ${filteredConsole.slice(0, 3).join(' | ')}`)

  await browser.close()
  if (failures.length) {
    console.log('RESULT: FAIL')
    failures.forEach((f) => console.log(' -', f))
    process.exit(1)
  }
  console.log('RESULT: PASS')
}

main().catch((e) => {
  console.error('RESULT: FAIL', e.message)
  process.exit(1)
})
