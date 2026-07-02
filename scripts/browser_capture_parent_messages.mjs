/**
 * Capture all API requests when opening /parent/messages.
 */
import { chromium } from 'playwright'
import { execSync } from 'child_process'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')

const accessToken = execSync('X:\\backend\\venv\\Scripts\\python.exe scripts/get_parent_token.py', {
  cwd: root,
  encoding: 'utf8',
}).trim()

async function main() {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({ accessToken: token, role: 'parent', viewerMode: 'parent', user: { id: 23, role: 'parent' } }),
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

  page.on('response', async (res) => {
    const req = res.request()
    if (!req.url().includes('/api/')) return
    const start = pending.get(req) ?? Date.now()
    pending.delete(req)
    let body = ''
    try {
      body = await res.text()
    } catch {
      body = '(unreadable)'
    }
    requests.push({
      method: req.method(),
      url: req.url(),
      path: req.url().replace(/^https?:\/\/[^/]+/, ''),
      status: res.status(),
      duration: Date.now() - start,
      body: body.slice(0, 1200),
    })
  })

  page.on('console', (msg) => {
    if (msg.type() === 'error') console.error('PAGE ERROR:', msg.text())
  })

  await page.goto('http://localhost:5173/parent/messages', { waitUntil: 'networkidle', timeout: 120000 })
  await page.waitForTimeout(2500)

  const errorBanner = await page.locator('.v-alert[type="error"]').first().textContent().catch(() => null)

  console.log('=== ERROR BANNER ===')
  console.log(errorBanner || '(none)')

  console.log('\n=== ALL API REQUESTS ===')
  for (const r of requests) {
    console.log(`${r.method} ${r.path.split('?')[0]} → ${r.status} (${r.duration}ms)`)
  }

  const failed = requests.filter((r) => r.status >= 400)
  console.log('\n=== FAILED REQUESTS (detail) ===')
  if (!failed.length) console.log('(none)')
  for (const r of failed) {
    console.log(`\n${r.method} ${r.path}`)
    console.log(`Status: ${r.status}`)
    console.log(`Body: ${r.body}`)
  }

  await browser.close()
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
