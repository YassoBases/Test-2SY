/** Quick parent page capture — 3 pages, 2s settle. */
import { chromium } from 'playwright'
import { execSync } from 'child_process'

const token = execSync('X:\\backend\\venv\\Scripts\\python.exe scripts/get_parent_token.py', { encoding: 'utf8' }).trim()
const pages = ['/parent/dashboard', '/parent/subjects-teachers', '/parent/student-reports', '/parent/messages']

const browser = await chromium.launch({ headless: true })
for (const path of pages) {
  const ctx = await browser.newContext()
  await ctx.addInitScript(({ t }) => {
    localStorage.setItem('eduspark_session', JSON.stringify({ accessToken: t, role: 'parent', viewerMode: 'parent' }))
    localStorage.setItem('eduspark_parent_selected_student', '5')
  }, { t: token })
  const page = await ctx.newPage()
  const apis = []
  page.on('response', (r) => {
    if (!r.url().includes('/api/')) return
    apis.push({ status: r.status(), url: r.url().replace(/student_id=\d+/, 'student_id={id}') })
  })
  await page.goto(`http://localhost:5173${path}`, { waitUntil: 'domcontentloaded', timeout: 30000 })
  await page.waitForTimeout(3000)
  const banner = await page.locator('.v-alert[type="error"]').first().textContent().catch(() => '')
  console.log(JSON.stringify({ path, banner: (banner || '').trim(), failed: apis.filter((a) => a.status >= 400), apis: apis.length }))
  await ctx.close()
}
await browser.close()
