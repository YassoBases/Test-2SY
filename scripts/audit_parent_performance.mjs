/**
 * Parent portal performance audit — captures API requests per page with timing.
 */
import { chromium } from 'playwright'
import { execSync } from 'child_process'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')

const pythonCandidates = [
  'X:\\backend\\venv\\Scripts\\python.exe',
  join(root, 'backend', 'venv', 'Scripts', 'python.exe'),
  join(root, 'backend', 'venv', 'bin', 'python'),
]

function resolvePython() {
  for (const candidate of pythonCandidates) {
    try {
      execSync(`"${candidate}" --version`, { stdio: 'ignore' })
      return candidate
    } catch {
      /* try next */
    }
  }
  throw new Error('No working Python found for get_parent_token.py')
}

const accessToken = execSync(`"${resolvePython()}" scripts/get_parent_token.py`, {
  cwd: root,
  encoding: 'utf8',
}).trim()

const PAGES = [
  { name: 'Dashboard', path: '/parent/dashboard', expect: ['GET /parent/students', 'GET /parent/dashboard'] },
  { name: 'Subjects & Teachers', path: '/parent/subjects-teachers', expect: ['GET /parent/students', 'GET /parent/subjects-teachers'] },
  { name: 'Reports', path: '/parent/student-reports', expect: ['GET /parent/students', 'GET /parent/historical-report'] },
  { name: 'Notifications', path: '/parent/student-notifications', expect: ['GET /parent/students', 'GET /parent/notifications', 'GET /parent/notification-settings'] },
  { name: 'AI Insights', path: '/parent/student-insights', expect: ['GET /parent/students', 'GET /parent/executive-summary'] },
  { name: 'Performance', path: '/parent/student-performance', expect: ['GET /parent/students', 'GET /parent/dashboard'] },
  { name: 'Lessons', path: '/parent/student-lessons', expect: ['GET /parent/students', 'GET /parent/dashboard'] },
  { name: 'Planner', path: '/parent/student-planner', expect: ['GET /parent/students', 'GET /parent/dashboard'] },
  { name: 'Attendance', path: '/parent/student-attendance', expect: ['GET /parent/students', 'GET /parent/dashboard', 'GET /parent/activity-tracking/analytics'] },
]

function normalizePath(url) {
  try {
    const u = new URL(url)
    return u.pathname.replace(/^\/api/, '') + u.search.replace(/student_id=\d+/, 'student_id={id}')
  } catch {
    return url
  }
}

function analyzePage(name, requests, expect = []) {
  const api = requests.filter((r) => r.url.includes('/api/') && !r.url.includes('/src/'))
  const byKey = new Map()
  for (const r of api) {
    const key = `${r.method} ${normalizePath(r.url)}`
    if (!byKey.has(key)) byKey.set(key, [])
    byKey.get(key).push(r)
  }
  const duplicates = [...byKey.entries()].filter(([, arr]) => arr.length > 1)

  const parentEndpoints = [...byKey.keys()].filter((k) => k.includes('/parent/'))
  const unexpectedParent = parentEndpoints.filter((k) => !expect.some((e) => k.startsWith(e)))
  const missingExpected = expect.filter((e) => !parentEndpoints.some((k) => k.startsWith(e)))

  return {
    name,
    totalApiRequests: api.length,
    parentApiRequests: parentEndpoints.length,
    uniqueEndpoints: byKey.size,
    expected: expect,
    unexpectedParent,
    missingExpected,
    duplicates: duplicates.map(([key, arr]) => ({
      endpoint: key,
      count: arr.length,
      durationsMs: arr.map((r) => Math.round(r.duration)),
    })),
    slow500ms: api.filter((r) => r.duration >= 500).map((r) => ({
      path: normalizePath(r.url),
      durationMs: Math.round(r.duration),
      status: r.status,
    })),
    slow1000ms: api.filter((r) => r.duration >= 1000).map((r) => ({
      path: normalizePath(r.url),
      durationMs: Math.round(r.duration),
    })),
    slow2000ms: api.filter((r) => r.duration >= 2000).map((r) => ({
      path: normalizePath(r.url),
      durationMs: Math.round(r.duration),
    })),
    endpoints: api
      .map((r) => ({
        method: r.method,
        path: normalizePath(r.url),
        status: r.status,
        durationMs: Math.round(r.duration),
      }))
      .sort((a, b) => b.durationMs - a.durationMs),
    wallClockSumMs: Math.round(api.reduce((s, r) => s + r.duration, 0)),
  }
}

async function capturePage(browser, pagePath) {
  const context = await browser.newContext()
  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({ accessToken: token, role: 'parent', viewerMode: 'parent' }),
    )
    localStorage.setItem('eduspark_parent_selected_student', '5')
  }, { token: accessToken })

  const page = await context.newPage()
  const requests = []
  const pending = new Map()

  page.on('request', (req) => {
    if (!req.url().includes('/api/')) return
    pending.set(req, Date.now())
  })

  page.on('response', (res) => {
    const req = res.request()
    if (!req.url().includes('/api/')) return
    const start = pending.get(req) ?? Date.now()
    pending.delete(req)
    requests.push({
      method: req.method(),
      url: req.url(),
      status: res.status(),
      duration: Date.now() - start,
    })
  })

  const t0 = Date.now()
  await page.goto(`http://localhost:5173${pagePath}`, { waitUntil: 'networkidle', timeout: 120000 })
  await page.waitForTimeout(2000)
  const wallMs = Date.now() - t0
  await context.close()
  return { requests, wallMs }
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const results = []

  for (const p of PAGES) {
    process.stderr.write(`Capturing ${p.name}...\n`)
    const { requests, wallMs } = await capturePage(browser, p.path)
    const analysis = analyzePage(p.name, requests, p.expect || [])
    analysis.wallClockMs = wallMs
    results.push(analysis)
  }

  await browser.close()

  const allHits = new Map()
  for (const r of results) {
    for (const e of r.endpoints) {
      const key = `${e.method} ${e.path}`
      if (!allHits.has(key)) allHits.set(key, [])
      allHits.get(key).push(e.durationMs)
    }
  }

  const top10Slowest = [...allHits.entries()]
    .map(([endpoint, times]) => ({
      endpoint,
      avgMs: Math.round(times.reduce((a, b) => a + b, 0) / times.length),
      maxMs: Math.max(...times),
      totalHits: times.length,
    }))
    .sort((a, b) => b.maxMs - a.maxMs)
    .slice(0, 10)

  console.log(JSON.stringify({ pages: results, top10Slowest }, null, 2))
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
