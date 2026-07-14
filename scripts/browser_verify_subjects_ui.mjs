/**
 * Verify ParentSubjectsTeachersView UI state: banner, subjectsError, loading.
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
      JSON.stringify({
        accessToken: token,
        refreshToken: 'browser-test',
        role: 'parent',
        viewerMode: 'parent',
        user: { id: 23, name: 'mother hamza', email: 'mother@gmail.com', role: 'parent' },
      }),
    )
    localStorage.setItem('eduspark_parent_selected_student', '5')
  }, { token: accessToken })

  const page = await context.newPage()
  const apiLog = []

  page.on('response', async (response) => {
    const url = response.url()
    if (!url.includes('/api/parent/subjects-teachers')) return
    apiLog.push({ status: response.status(), url })
  })

  page.on('console', (msg) => {
    if (msg.text().includes('[subjects-teachers]')) {
      console.log('BROWSER LOG:', msg.text())
    }
  })

  await page.goto('http://localhost:5173/parent/subjects-teachers', {
    waitUntil: 'networkidle',
    timeout: 60000,
  })
  await page.waitForTimeout(3000)

  const ui = await page.evaluate(() => {
    const errorAlert = document.querySelector('.v-alert.text-error, .v-alert--variant-tonal[type="error"]')
    const anyAlert = [...document.querySelectorAll('.v-alert')].map((el) => ({
      type: el.getAttribute('type'),
      text: el.textContent?.trim().slice(0, 200),
      visible: el.offsetParent !== null,
    }))
    const skeleton = document.querySelector('.v-skeleton-loader')
    const section = document.querySelector('.parent-subjects-section, [class*="subjects"]')
    return {
      errorBannerVisible: !!errorAlert && errorAlert.offsetParent !== null,
      errorBannerText: errorAlert?.textContent?.trim() ?? null,
      allAlerts: anyAlert,
      skeletonVisible: !!skeleton && skeleton.offsetParent !== null,
      hasContent: !!document.body.innerText.match(/فيزياء|ياسر|مسجّل|متاح/),
      bodySnippet: document.body.innerText.slice(0, 500),
    }
  })

  console.log('\n=== subjects-teachers API calls ===')
  apiLog.forEach((r) => console.log(`${r.status} ${r.url}`))

  console.log('\n=== UI STATE ===')
  console.log(JSON.stringify(ui, null, 2))

  await browser.close()
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
