/**
 * Race: first subjects-teachers request hangs on 422, page reload triggers second 200.
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
  let n = 0

  await context.route('**/api/parent/subjects-teachers**', async (route) => {
    n += 1
    if (n === 1) {
      await new Promise((r) => setTimeout(r, 3000))
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({ detail: [{ loc: ['query', 'student_id'], msg: 'stale 422' }] }),
      })
      return
    }
    await route.continue()
  })

  await context.addInitScript(({ token }) => {
    localStorage.setItem(
      'eduspark_session',
      JSON.stringify({ accessToken: token, role: 'parent', viewerMode: 'parent' }),
    )
    localStorage.setItem('eduspark_parent_selected_student', '5')
  }, { token: accessToken })

  const page = await context.newPage()
  page.on('console', (msg) => {
    if (msg.text().includes('[subjects-teachers]')) console.log(msg.text())
  })

  await page.goto('http://localhost:5173/parent/subjects-teachers', { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(500)
  await page.reload({ waitUntil: 'networkidle', timeout: 90000 })
  await page.waitForTimeout(4000)

  const ui = await page.evaluate(() => ({
    errorAlerts: [...document.querySelectorAll('.v-alert')].map((el) => ({
      type: el.getAttribute('type'),
      text: el.textContent?.trim(),
    })),
    hasPhysics: document.body.innerText.includes('فيزياء'),
  }))

  console.log('Total API calls:', n)
  console.log('UI:', JSON.stringify(ui, null, 2))
  const redError = ui.errorAlerts.find((a) => a.type === 'error')
  console.log('Red banner after race:', redError ?? '(none)')
  await browser.close()
  process.exit(redError ? 1 : 0)
}

main()
