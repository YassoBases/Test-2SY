import { chromium } from 'playwright'
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage()
await page.goto('http://localhost:5173/login?entry=welcome', { waitUntil: 'networkidle', timeout: 60000 })
console.log('URL:', page.url())
console.log('TITLE:', await page.title())
console.log('HTML snippet:', (await page.content()).slice(0, 2000))
await page.screenshot({ path: '.tmp-login-debug.png', fullPage: true })
await browser.close()
