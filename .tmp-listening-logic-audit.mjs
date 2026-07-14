import { request as playwrightRequest } from 'playwright'

const API = 'http://127.0.0.1:8000'
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
  return data.access_token
}

async function get(token, path) {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.get(path, { headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' } })
  const json = await res.json().catch(() => ({}))
  await ctx.dispose()
  return { status: res.status(), json }
}

const failures = []

for (const [key, email] of PERSONAS) {
  const token = await login(email)
  const memory = await get(token, '/api/student/languages/learner/memory')
  const status = await get(token, '/api/student/languages/listening/promotion-test/status')
  const next = await get(token, '/api/student/languages/listening/next')

  console.log(`\n=== Persona ${key} ===`)
  console.log('memory GET', memory.status)
  console.log('next GET', next.status)

  if (next.status === 404) {
    failures.push(`${key}: listening/next 404 — ${next.json.detail}`)
    continue
  }
  if (next.status >= 400) {
    failures.push(`${key}: listening/next ${next.status}`)
    continue
  }

  const official = status.json?.readiness?.official_cefr || status.json?.eligibility?.official_cefr
  const lesson = next.json
  const coach = lesson.coach || {}
  const memoryGoals = memory.json?.learning_goals || []

  console.log('Official Level:', official)
  console.log('Lesson Level:', lesson.level)
  console.log('Lesson Topic:', lesson.title)
  console.log('Memory goals:', memoryGoals)
  console.log('Lesson goal (coach):', coach.learning_goal, coach.learning_goal_label)
  console.log('Situation:', coach.situation, coach.situation_label)
  console.log('Reason:', coach.coach_why)
  console.log('Focus:', coach.coach_focus)
  console.log('Reward:', coach.coach_reward)
  if (coach.level_mismatch) console.log('Level note:', coach.level_mismatch_reason)

  if (!coach.learning_goal) {
    failures.push(`${key}: lesson missing coach.learning_goal metadata`)
  }
  if (!coach.coach_why || coach.coach_why.includes('regular practice is the fastest')) {
    failures.push(`${key}: coach_why looks generic or missing`)
  }
  if (lesson.title?.toLowerCase().includes('work stress') && coach.learning_goal !== 'business') {
    failures.push(`${key}: Work Stress lesson but goal=${coach.learning_goal}`)
  }
}

console.log('\n=== RESULT ===')
if (failures.length) {
  console.log('FAIL')
  for (const f of failures) console.log(' -', f)
  process.exit(1)
}
console.log('PASS')
