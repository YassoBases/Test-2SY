/**
 * Capture all API requests when loading /parent/subjects-teachers (browser Network tab equivalent).
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

const requests = []

async function main() {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({
        accessToken: token,
        refreshToken: 'browser-test',
        role: 'parent',
        viewerMode: 'parent',
        user: { id: 23, name: 'mother hamza', email: 'mother@gmail.com', role: 'parent' },
      }),
    )
  }, { token: accessToken })

  const page = await context.newPage()

  page.on('response', async (response) => {
    const url = response.url()
    if (!url.includes('/api/')) return
    const path = url.replace(/^https?:\/\/[^/]+/, '')
    let body = ''
    try {
      body = await response.text()
    } catch {
      body = '(unreadable)'
    }
    requests.push({
      method: response.request().method(),
      path,
      status: response.status(),
      body: body.slice(0, 800),
    })
  })

  await page.goto('http://localhost:5173/parent/subjects-teachers', {
    waitUntil: 'networkidle',
    timeout: 60000,
  })
  await page.waitForTimeout(2500)

  const errorAlerts = await page.locator('.v-alert').allTextContents()

  console.log('=== PAGE ALERTS ===')
  console.log(errorAlerts.join('\n---\n') || '(none)')

  console.log('\n=== ALL API REQUESTS (sorted) ===')
  const seen = new Set()
  for (const r of requests) {
    const key = `${r.method} ${r.path.split('?')[0]}`
    if (seen.has(key)) continue
    seen.add(key)
    console.log(`${r.method} ${r.path} -> ${r.status}`)
  }

  console.log('\n=== FULL REQUEST LIST ===')
  for (const r of requests) {
    console.log(`${r.method} ${r.path} -> ${r.status}`)
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
