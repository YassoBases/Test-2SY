import { chromium, request as playwrightRequest } from 'playwright'

const API = 'http://127.0.0.1:8000'
const BASE = 'http://127.0.0.1:5173'
const PASSWORD = 'TestOnly123!'

const PERSONAS = [
  ['A', 'qa.listening.student-a@eduspark-test.dev'],
  ['B', 'qa.listening.student-b@eduspark-test.dev'],
  ['C', 'qa.listening.student-c@eduspark-test.dev'],
  ['D', 'qa.listening.student-d@eduspark-test.dev'],
  ['E', 'qa.listening.student-e@eduspark-test.dev'],
]

async function login(email) {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.post('/api/auth/login', { data: { email, password: PASSWORD } })
  const data = await res.json()
  await ctx.dispose()
  return { ...data.user, accessToken: data.access_token, refreshToken: data.refresh_token, loggedInAt: new Date().toISOString(), onboardingComplete: true }
}

async function apiGet(token, path) {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.get(path, { headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' } })
  const body = await res.text()
  let json = null
  try { json = JSON.parse(body) } catch {}
  await ctx.dispose()
  return { path, status: res.status(), json, raw: body.slice(0, 300) }
}

async function auditPersona(key, email) {
  const session = await login(email)
  const token = session.accessToken
  const calls = await Promise.all([
    apiGet(token, '/api/student/languages/hub'),
    apiGet(token, '/api/student/languages/learner/memory'),
    apiGet(token, '/api/student/languages/listening/promotion-test/status'),
    apiGet(token, '/api/student/languages/listening/next'),
    apiGet(token, '/api/student/languages/listening'),
  ])

  const fails = calls.filter((c) => c.status >= 400)
  const next = calls.find((c) => c.path.endsWith('/next'))
  const memory = calls.find((c) => c.path.includes('memory'))
  const status = calls.find((c) => c.path.includes('status'))

  console.log(`\n=== Persona ${key} (${email}) ===`)
  for (const c of calls) {
    console.log(`${c.status} ${c.path}`)
    if (c.status >= 400) console.log('  detail:', c.raw)
  }

  const official = status?.json?.readiness?.official_cefr || status?.json?.eligibility?.official_cefr || '—'
  const lesson = next?.json || null
  console.log('Official CEFR:', official)
  console.log('Memory goals:', memory?.json?.learning_goals)
  if (lesson) {
    console.log('Lesson:', { id: lesson.id, title: lesson.title, level: lesson.level, keys: Object.keys(lesson) })
    if (lesson.context) console.log('Context:', JSON.stringify(lesson.context, null, 2))
  }

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ locale: 'en-US' })
  await context.addInitScript((s) => {
    localStorage.setItem('eduspark_session', JSON.stringify(s))
    localStorage.setItem('eduspark-locale', 'en')
  }, session)
  const page = await context.newPage()
  const network404 = []
  page.on('response', (res) => {
    if (res.status() === 404) network404.push({ url: res.url(), method: res.request().method() })
  })
  await page.goto(`${BASE}/student/languages/listening?tab=practice`, { waitUntil: 'networkidle', timeout: 120000 })
  await page.waitForTimeout(2000)
  if (network404.length) {
    console.log('Browser 404s:')
    for (const n of network404) console.log(`  ${n.method} ${n.url}`)
  } else {
    console.log('Browser 404s: none')
  }
  await browser.close()

  return { key, fails, network404, official, lesson, memoryGoals: memory?.json?.learning_goals }
}

const results = []
for (const [k, e] of PERSONAS) {
  try {
    results.push(await auditPersona(k, e))
  } catch (err) {
    console.error(`Persona ${k} error:`, err.message)
    results.push({ key: k, error: err.message })
  }
}

console.log('\n=== SUMMARY ===')
for (const r of results) {
  const apiFails = r.fails?.length || 0
  const b404 = r.network404?.length || 0
  console.log(`${r.key}: api_errors=${apiFails} browser_404=${b404}${r.error ? ` err=${r.error}` : ''}`)
}
