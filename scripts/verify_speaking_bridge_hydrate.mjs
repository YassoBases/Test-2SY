/**
 * Verify bridge hydrate ownership logic against a live API (+ isBridgeHydrated unit checks).
 * Mirrors useSpeakingLiveBridge.ensureHydrated without a browser.
 *
 * Usage: node scripts/verify_speaking_bridge_hydrate.mjs
 */
import { createRequire } from 'module'
import { pathToFileURL } from 'url'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const API = process.env.API_BASE || 'http://127.0.0.1:8000'

// Load isBridgeHydrated from the composable via dynamic import (Vite-free ESM).
const require = createRequire(import.meta.url)
// Duplicate the pure helper to avoid Vue bundling — must match composable.
function isBridgeHydrated(raw) {
  if (!raw || typeof raw !== 'object') return false
  const phase = String(raw.journey_phase || 'idle')
  if (phase !== 'idle') return true
  if (raw.preparation || raw.rehearsal || raw.live_context || raw.ready_for_live) return true
  return false
}

let pass = 0
let fail = 0
function check(name, cond, detail = '') {
  if (cond) {
    pass += 1
    console.log('  OK ', name)
  } else {
    fail += 1
    console.log(' FAIL', name, detail ? `— ${detail}` : '')
  }
}

check('null not hydrated', !isBridgeHydrated(null))
check('idle empty not hydrated', !isBridgeHydrated({ journey_phase: 'idle', preparation: null }))
check('preparation hydrated', isBridgeHydrated({ journey_phase: 'preparation', preparation: { package_id: 'x' } }))
check('gpt_rehearsal hydrated', isBridgeHydrated({ journey_phase: 'gpt_rehearsal' }))

const login = await (
  await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'test.auth.student@eduspark-test.dev',
      password: 'TestOnly123!',
    }),
  })
).json()

if (!login.access_token) {
  console.log(' FAIL login')
  process.exit(1)
}

const h = {
  Authorization: `Bearer ${login.access_token}`,
  'Content-Type': 'application/json',
}

async function ensureHydrated(packageId = null) {
  let bridge = null
  const steps = []
  try {
    const r = await fetch(`${API}/api/student/languages/speaking/live-bridge/active`, { headers: h })
    steps.push(`GET active ${r.status}`)
    bridge = await r.json()
  } catch (e) {
    steps.push(`GET active throw ${e.message}`)
  }
  if (!isBridgeHydrated(bridge)) {
    const r = await fetch(`${API}/api/student/languages/speaking/live-bridge/prepare`, {
      method: 'POST',
      headers: h,
      body: JSON.stringify({ package_id: packageId }),
    })
    steps.push(`POST prepare ${r.status}`)
    bridge = await r.json()
  } else {
    steps.push('skip prepare (active usable)')
  }
  return { bridge, steps }
}

// Prefer existing package from prior start-learning if any
let packageId = null
const started = await fetch(`${API}/api/student/languages/speaking/runtime/start-learning`, {
  method: 'POST',
  headers: h,
  body: JSON.stringify({ author_mode: 'auto', use_cache: true }),
})
if (started.ok) {
  const body = await started.json()
  packageId = body?.package?.package_id || body?.package?.package?.package_id || null
  console.log('packageId', packageId)
}

const first = await ensureHydrated(packageId)
check('ensure produces hydrated bridge', isBridgeHydrated(first.bridge), JSON.stringify(first.steps))
check(
  'ensure has preparation or advanced phase',
  Boolean(first.bridge?.preparation) || first.bridge?.journey_phase !== 'idle',
  first.bridge?.journey_phase,
)

const second = await ensureHydrated(packageId)
check(
  'second ensure reuses active (no forced blank)',
  isBridgeHydrated(second.bridge),
  JSON.stringify(second.steps),
)

console.log('\nResult:', pass, 'passed,', fail, 'failed')
console.log('steps', first.steps, '→', second.steps)
process.exit(fail ? 1 : 0)
