/**
 * Parent portal root-cause investigation — browser evidence capture.
 * Usage: node scripts/investigate_parent_portal.mjs
 */
import { chromium } from 'playwright'
import { execSync } from 'child_process'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { writeFileSync } from 'fs'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')

const pythonCandidates = [
  'X:\\backend\\venv\\Scripts\\python.exe',
  join(root, 'backend', 'venv', 'Scripts', 'python.exe'),
]

function resolvePython() {
  for (const c of pythonCandidates) {
    try {
      execSync(`"${c}" --version`, { stdio: 'ignore' })
      return c
    } catch {
      /* next */
    }
  }
  throw new Error('No Python for token')
}

const accessToken = execSync(`"${resolvePython()}" scripts/get_parent_token.py`, {
  cwd: root,
  encoding: 'utf8',
}).trim()

const PAGES = [
  { name: 'dashboard', path: '/parent/dashboard' },
  { name: 'subjects-teachers', path: '/parent/subjects-teachers' },
  { name: 'reports', path: '/parent/student-reports' },
  { name: 'notifications', path: '/parent/student-notifications' },
  { name: 'insights', path: '/parent/student-insights' },
  { name: 'performance', path: '/parent/student-performance' },
  { name: 'lessons', path: '/parent/student-lessons' },
  { name: 'planner', path: '/parent/student-planner' },
  { name: 'attendance', path: '/parent/student-attendance' },
  { name: 'messages', path: '/parent/messages' },
  { name: 'link', path: '/parent/link' },
]

function normalizeUrl(url) {
  try {
    const u = new URL(url)
    return u.pathname.replace(/^\/api/, '') + u.search.replace(/student_id=\d+/g, 'student_id={id}')
  } catch {
    return url
  }
}

async function capturePage(browser, pageDef, opts = {}) {
  const context = await browser.newContext()
  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({ accessToken: token, role: 'parent', viewerMode: 'parent' }),
    )
    localStorage.setItem('eduspark_parent_selected_student', '5')
    localStorage.setItem('eduspark_parent_debug', '1')
    window.__parentDebugLog = []
  }, { token: accessToken })

  const page = await context.newPage()
  const requests = []
  const pending = new Map()

  page.on('console', (msg) => {
    if (msg.text().includes('[parent-debug]')) {
      requests.push({ type: 'debug-log', text: msg.text() })
    }
  })

  page.on('request', (req) => {
    if (!req.url().includes('/api/')) return
    pending.set(req, Date.now())
  })

  page.on('response', async (res) => {
    const req = res.request()
    if (!req.url().includes('/api/')) return
    const start = pending.get(req) ?? Date.now()
    pending.delete(req)
    let bodyPreview = ''
    if (res.status() >= 400) {
      try {
        bodyPreview = (await res.text()).slice(0, 300)
      } catch {
        bodyPreview = ''
      }
    }
    requests.push({
      type: 'api',
      method: req.method(),
      url: normalizeUrl(req.url()),
      status: res.status(),
      durationMs: Date.now() - start,
      bodyPreview,
    })
  })

  if (opts.prefetch) {
    await page.goto(`http://localhost:5173${opts.prefetch}`, { waitUntil: 'networkidle', timeout: 120000 })
    await page.waitForTimeout(500)
  }

  const navStart = Date.now()
  await page.goto(`http://localhost:5173${pageDef.path}`, { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(4000)

  const errorBanner = await page.locator('.parent-portal-page .v-alert--variant-tonal.text-error, .parent-portal-page .v-alert[type="error"]').first().textContent().catch(() => '')
  const warningBanner = await page.locator('.parent-portal-page .v-alert[type="warning"]').first().textContent().catch(() => '')
  const anyErrorAlert = await page.locator('.v-alert[type="error"]').first().textContent().catch(() => '')

  const debugLog = await page.evaluate(() => window.__parentDebugLog || [])

  const apiCalls = requests.filter((r) => r.type === 'api')
  const failed = apiCalls.filter((r) => r.status >= 400)
  const objectObject = apiCalls.filter((r) => r.url.includes('[object') || r.url.includes('object%20Object'))

  await context.close()

  return {
    page: pageDef.name,
    path: pageDef.path,
    wallMs: Date.now() - navStart,
    errorBanner: (errorBanner || '').trim(),
    warningBanner: (warningBanner || '').trim(),
    anyErrorAlert: (anyErrorAlert || '').trim(),
    apiCalls,
    failedRequests: failed,
    objectObjectUrls: objectObject,
    debugLog,
    totalApi: apiCalls.length,
  }
}

async function rapidStudentSwitch(browser) {
  const context = await browser.newContext()
  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({ accessToken: token, role: 'parent', viewerMode: 'parent' }),
    )
    localStorage.setItem('eduspark_parent_selected_student', '5')
    localStorage.setItem('eduspark_parent_debug', '1')
  }, { token: accessToken })

  const page = await context.newPage()
  const requests = []
  page.on('response', (res) => {
    const url = res.request().url()
    if (!url.includes('/api/parent/')) return
    requests.push({ url: normalizeUrl(url), status: res.status(), method: res.request().method() })
  })

  await page.goto('http://localhost:5173/parent/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(1000)

  // Rapid navigation without waiting
  for (const p of ['/parent/student-reports', '/parent/subjects-teachers', '/parent/student-insights', '/parent/dashboard']) {
    page.goto(`http://localhost:5173${p}`).catch(() => {})
    await page.waitForTimeout(300)
  }
  await page.waitForTimeout(4000)

  const errorBanner = await page.locator('.parent-portal-page .v-alert[type="error"]').first().textContent().catch(() => '')
  const failed = requests.filter((r) => r.status >= 400)

  await context.close()
  return { scenario: 'rapid-navigation', parentRequests: requests.length, failedRequests: failed, errorBanner: (errorBanner || '').trim() }
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const results = { capturedAt: new Date().toISOString(), pages: [], scenarios: [] }

  for (const p of PAGES) {
    process.stderr.write(`Investigating ${p.name}...\n`)
    results.pages.push(await capturePage(browser, p))
  }

  process.stderr.write('Rapid navigation scenario...\n')
  results.scenarios.push(await rapidStudentSwitch(browser))

  await browser.close()

  const reportPath = join(root, 'scripts', 'parent_portal_investigation.json')
  writeFileSync(reportPath, JSON.stringify(results, null, 2), 'utf8')
  console.log(JSON.stringify(results, null, 2))
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
