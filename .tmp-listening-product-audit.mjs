/**
 * Listening Product Logic Audit — browser + API
 * Read-only verification. Does not mutate data except loading lessons.
 */
import { chromium, request as playwrightRequest } from 'playwright'

const BASE = 'http://127.0.0.1:5173'
const API = 'http://127.0.0.1:8000'
const PASSWORD = 'TestOnly123!'

const PERSONAS = [
  ['A', 'qa.listening.student-a@eduspark-test.dev'],
  ['B', 'qa.listening.student-b@eduspark-test.dev'],
  ['C', 'qa.listening.student-c@eduspark-test.dev'],
  ['D', 'qa.listening.student-d@eduspark-test.dev'],
  ['E', 'qa.listening.student-e@eduspark-test.dev'],
  ['F', 'qa.listening.student-f@eduspark-test.dev'],
  ['G', 'qa.listening.student-g@eduspark-test.dev'],
]

const GOAL_TOPIC_HINTS = {
  travel: ['travel', 'airport', 'hotel', 'trip', 'flight', 'tour', 'directions', 'passport'],
  business: ['business', 'work', 'office', 'meeting', 'stress', 'interview', 'professional', 'colleague'],
  daily_life: ['daily', 'home', 'market', 'shop', 'neighbor', 'family', 'routine'],
  conversation: ['conversation', 'dialogue', 'chat', 'discussion'],
  job_interview: ['interview', 'job', 'hiring', 'resume'],
  ielts: ['ielts', 'exam', 'test', 'academic'],
  general_english: [],
}

const findings = []
const apiErrors = []
const lessonsAudited = []

function finding(severity, category, persona, message, rootHint = '') {
  findings.push({ severity, category, persona, message, rootHint })
}

async function login(email) {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.post('/api/auth/login', { data: { email, password: PASSWORD } })
  if (!res.ok()) throw new Error(`Login failed ${email}: ${res.status()}`)
  const data = await res.json()
  await ctx.dispose()
  return {
    ...data.user,
    accessToken: data.access_token,
    refreshToken: data.refresh_token || null,
    loggedInAt: new Date().toISOString(),
    onboardingComplete: true,
  }
}

async function apiGet(token, path) {
  const ctx = await playwrightRequest.newContext({ baseURL: API })
  const res = await ctx.get(path, { headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' } })
  let json = null
  try { json = await res.json() } catch { /* */ }
  await ctx.dispose()
  return { path, status: res.status(), json }
}

function goalMatchesTopic(goalId, title, situation) {
  if (!goalId) return { ok: false, reason: 'no goal id' }
  const text = `${title || ''} ${situation || ''}`.toLowerCase()
  const hints = GOAL_TOPIC_HINTS[goalId] || []
  if (!hints.length) return { ok: true, reason: 'general goal' }
  const hit = hints.some((h) => text.includes(h))
  return { ok: hit, reason: hit ? 'topic aligns' : `no keyword match for ${goalId} in "${text.slice(0, 80)}"` }
}

function auditLessonFromApi(persona, memoryGoals, status, lesson) {
  if (!lesson?.id) return null
  const coach = lesson.coach || {}
  const official =
    status?.readiness?.official_cefr || status?.eligibility?.official_cefr || coach.official_cefr
  const record = {
    persona,
    lessonId: lesson.id,
    title: lesson.title,
    lessonLevel: lesson.level,
    officialCefr: official,
    memoryGoals,
    coachGoal: coach.learning_goal,
    coachGoalLabel: coach.learning_goal_label,
    situation: coach.situation,
    situationLabel: coach.situation_label,
    coachWhy: coach.coach_why,
    coachFocus: coach.coach_focus || [],
    coachReward: coach.coach_reward,
    levelMismatch: coach.level_mismatch,
    levelMismatchReason: coach.level_mismatch_reason,
    objectives: coach.objectives || [],
    difficulty: coach.difficulty_band,
    challengeLevel: coach.challenge_level,
  }
  lessonsAudited.push(record)

  // 1. CEFR consistency
  if (official && lesson.level && official.toUpperCase() !== String(lesson.level).toUpperCase()) {
    if (!coach.level_mismatch || !coach.level_mismatch_reason) {
      finding(
        'critical',
        'cefr_mismatch',
        persona,
        `Official ${official} but lesson level ${lesson.level} with NO acceptable explanation`,
        'Stale pool item, missing level_mismatch in coach context, or wrong pool filter',
      )
    } else {
      const reason = coach.level_mismatch_reason.toLowerCase()
      const acceptable = ['promotion', 'challenge', 'review', 'harder', 'easier', 'stretch', 'confidence'].some(
        (w) => reason.includes(w),
      )
      if (!acceptable) {
        finding(
          'major',
          'cefr_mismatch',
          persona,
          `Official ${official} vs lesson ${lesson.level}; explanation "${coach.level_mismatch_reason}" may not meet product rules`,
          'level_mismatch_reason not aligned to Promotion Test / Challenge / Review taxonomy',
        )
      }
    }
  }

  // 2. Goal vs topic
  const goalCheck = goalMatchesTopic(coach.learning_goal, lesson.title, coach.situation_label || coach.situation)
  if (!goalCheck.ok) {
    finding(
      'critical',
      'goal_topic_mismatch',
      persona,
      `Lesson "${lesson.title}" has goal=${coach.learning_goal} but topic does not align (${goalCheck.reason})`,
      'Goal engine selected goal not reflected in generated title/situation OR coach reads wrong goal',
    )
  }

  // 3. Mission - generic phrases
  const genericPhrases = [
    'regular practice is the fastest',
    'Build confidence for everyday',
    'because regular practice',
    'defaultWhy',
    'student.languages.',
  ]
  const why = coach.coach_why || ''
  for (const g of genericPhrases) {
    if (why.toLowerCase().includes(g.toLowerCase())) {
      finding('major', 'mission_generic', persona, `Generic coach_why: "${why.slice(0, 120)}"`, 'Fallback copy or template in lesson context builder')
    }
  }
  // Travel in mission when lesson is work/business
  const titleLow = (lesson.title || '').toLowerCase()
  if ((titleLow.includes('work') || titleLow.includes('business') || titleLow.includes('stress')) && why.toLowerCase().includes('travel')) {
    finding('critical', 'mission_contradiction', persona, `Work/business lesson but coach_why mentions travel: "${why}"`, 'Frontend using memory goal or stale coach text')
  }

  // 4. Coach focus must reference lesson specifics
  if (!coach.coach_focus?.length) {
    finding('major', 'coach_empty_focus', persona, `Lesson ${lesson.id} has empty coach_focus`, 'Missing curriculum/objectives in body_json')
  }
  if (!coach.coach_why) {
    finding('critical', 'coach_missing_why', persona, `Lesson ${lesson.id} missing coach_why`, 'API coach builder or missing metadata')
  }

  return record
}

async function auditPersona(browser, key, email) {
  console.log(`\n========== Persona ${key} ==========`)
  const session = await login(email)
  const token = session.accessToken

  const endpoints = [
    '/api/student/languages/hub',
    '/api/student/languages/learner/memory',
    '/api/student/languages/listening/promotion-test/status',
    '/api/student/languages/listening/next',
    '/api/student/languages/listening',
  ]
  const apiResults = {}
  for (const path of endpoints) {
    const r = await apiGet(token, path)
    apiResults[path] = r
    if (r.status === 404 || r.status === 422 || r.status === 500) {
      apiErrors.push({ persona: key, path, status: r.status, detail: r.json?.detail || r.json })
      finding(
        r.status >= 500 ? 'critical' : 'major',
        'api_error',
        key,
        `${r.status} ${path}: ${JSON.stringify(r.json?.detail || r.json).slice(0, 200)}`,
        'Empty pool, generation failure, or route/data issue',
      )
    }
  }

  const status = apiResults['/api/student/languages/listening/promotion-test/status']?.json
  const memory = apiResults['/api/student/languages/learner/memory']?.json
  const nextLesson = apiResults['/api/student/languages/listening/next']?.json

  if (nextLesson?.id) {
    auditLessonFromApi(key, memory?.learning_goals, status, nextLesson)
  }

  // Browser
  const context = await browser.newContext({ locale: 'en-US' })
  await context.addInitScript((s) => {
    localStorage.setItem('eduspark_session', JSON.stringify(s))
    localStorage.setItem('eduspark-locale', 'en')
  }, session)
  const page = await context.newPage()

  const browserApiErrors = []
  const axiosLikeErrors = []
  page.on('response', (res) => {
    const url = res.url()
    if (!url.includes('/api/')) return
    const st = res.status()
    if (st === 404 || st === 422 || st === 500) {
      browserApiErrors.push({ url, status: st, method: res.request().method() })
    }
  })
  page.on('console', (msg) => {
    const t = msg.text()
    if (msg.type() === 'error' && (t.includes('404') || t.includes('422') || t.includes('500') || t.includes('Axios') || t.includes('Network Error'))) {
      axiosLikeErrors.push(t.slice(0, 200))
    }
  })

  await page.goto(`${BASE}/student/languages/listening`, { waitUntil: 'networkidle', timeout: 120000 })
  await page.waitForTimeout(2000)
  const journeyText = await page.locator('body').innerText()

  // Journey official level from hero
  const heroOfficialMatch = journeyText.match(/Official level[\s\S]{0,30}?(\A[12]|B[12]|C[12])/i)
  const promotionOfficial = status?.readiness?.official_cefr || status?.eligibility?.official_cefr

  // Practice tab
  await page.locator('.v-tab').filter({ hasText: /practice/i }).first().click()
  await page.waitForTimeout(1500)

  const startBtn = page.getByRole('button', { name: /start listening/i }).first()
  if (await startBtn.isVisible().catch(() => false)) {
    await startBtn.click()
    await page.waitForTimeout(6000)

    const practiceText = await page.locator('body').innerText()
    const uiLesson = {
      hasMission: /today'?s mission/i.test(practiceText),
      hasWhy: /why\?/i.test(practiceText),
      bodySnippet: practiceText.slice(0, 2500),
    }

    // Compare UI goal row vs API
    if (nextLesson?.coach?.learning_goal) {
      const goalId = nextLesson.coach.learning_goal
      const goalLabels = {
        travel: /travel/i,
        business: /business/i,
        daily_life: /daily life/i,
        conversation: /conversation/i,
      }
      const pattern = goalLabels[goalId]
      if (pattern && !pattern.test(practiceText)) {
        finding(
          'critical',
          'ui_goal_mismatch',
          key,
          `API goal=${goalId} but Practice UI may not show matching goal label`,
          'ListeningPracticePanel / coachLessonMetaRows not using lesson.coach',
        )
      }
      // Memory goal shown incorrectly?
      for (const mem of memory?.learning_goals || []) {
        if (/travel/i.test(mem) && goalId !== 'travel' && /travel/i.test(practiceText) && !/business|work/i.test(nextLesson.title || '')) {
          finding(
            'critical',
            'ui_memory_goal_leak',
            key,
            `Memory mentions travel but lesson goal is ${goalId}; Travel visible in UI`,
            'useListeningJourney.activeGoalId used instead of lesson.coach.learning_goal',
          )
        }
      }
    }

    // Hardcoded i18n keys visible
    if (/student\.languages/.test(practiceText)) {
      finding('critical', 'i18n_leak', key, 'Raw i18n keys visible on Practice tab', 'Missing translation key')
    }

    // Generic mission fallback visible
    if (/because regular practice is the fastest/i.test(practiceText)) {
      finding('major', 'ui_generic_mission', key, 'Generic defaultWhy visible in browser', 'coach_why fallback')
    }

    lessonsAudited.push({ persona: key, source: 'browser_practice', ui: uiLesson, apiTitle: nextLesson?.title })
  } else {
    const errAlert = await page.locator('.v-alert').allInnerTexts().catch(() => [])
    if (errAlert.some((t) => /404|not found|could not load|no listening/i.test(t))) {
      finding('major', 'ui_load_error', key, `Practice could not start: ${errAlert.join(' ').slice(0, 150)}`, 'listening/next 404 surfaced to student')
    }
  }

  // Promotion tab
  await page.locator('.v-tab').filter({ hasText: /promotion/i }).first().click()
  await page.waitForTimeout(2000)
  const promoText = await page.locator('body').innerText()

  // Progress consistency: hero vs promotion
  if (promotionOfficial && journeyText.includes('Official level')) {
    if (!journeyText.includes(promotionOfficial)) {
      finding(
        'major',
        'progress_contradiction',
        key,
        `Journey hero may not show official CEFR ${promotionOfficial}`,
        'officialCefr computed from different source than promotion status',
      )
    }
  }

  if (browserApiErrors.length) {
    for (const e of browserApiErrors) {
      apiErrors.push({ persona: key, ...e })
      finding('major', 'browser_api_error', key, `Browser saw ${e.status} ${e.method} ${e.url}`, 'Failed API during navigation')
    }
  }
  if (axiosLikeErrors.length) {
    for (const e of axiosLikeErrors) {
      finding('major', 'console_error', key, `Console: ${e}`, 'Unhandled API error in frontend')
    }
  }

  // Hardcoded repeated strings check on journey
  const repeatedPatterns = ['Promotion Readiness', 'Transition Gate', 'Confidence Engine', 'Evidence Engine', 'Stage Score']
  for (const p of repeatedPatterns) {
    if (journeyText.includes(p) || promoText.includes(p)) {
      finding('critical', 'jargon_leak', key, `Internal jargon visible: "${p}"`, 'Coach sanitization incomplete')
    }
  }

  await context.close()
  return { key, apiResults, browserApiErrors }
}

const browser = await chromium.launch({ headless: true })
for (const [k, e] of PERSONAS) {
  try {
    await auditPersona(browser, k, e)
  } catch (err) {
    finding('critical', 'audit_crash', k, err.message, 'Test infrastructure or login failure')
  }
}
await browser.close()

// Cross-lesson: detect repeated identical coach_why (template detection)
const whyCounts = {}
for (const l of lessonsAudited) {
  if (l.coachWhy) {
    whyCounts[l.coachWhy] = (whyCounts[l.coachWhy] || 0) + 1
  }
}
for (const [why, count] of Object.entries(whyCounts)) {
  if (count >= 3) {
    finding(
      'major',
      'coach_template',
      'ALL',
      `Identical coach_why repeated ${count} times: "${why.slice(0, 100)}..."`,
      'language_listening_lesson_context.py template formula same for all lessons',
    )
  }
}

console.log('\n\n========== AUDIT SUMMARY ==========')
console.log('Lessons audited:', lessonsAudited.length)
console.log('API errors:', apiErrors.length)
console.log('Findings:', findings.length)

const bySeverity = { critical: [], major: [], minor: [] }
for (const f of findings) {
  bySeverity[f.severity]?.push(f)
}

console.log('\nCRITICAL:', bySeverity.critical.length)
bySeverity.critical.forEach((f) => console.log(`  [${f.persona}] ${f.category}: ${f.message}`))

console.log('\nMAJOR:', bySeverity.major.length)
bySeverity.major.forEach((f) => console.log(`  [${f.persona}] ${f.category}: ${f.message}`))

// Write JSON report
import fs from 'fs'
const report = {
  auditedAt: new Date().toISOString(),
  lessonsAudited,
  apiErrors,
  findings,
  summary: {
    critical: bySeverity.critical.length,
    major: bySeverity.major.length,
    minor: bySeverity.minor.length,
  },
}
fs.writeFileSync('.tmp-listening-product-audit.json', JSON.stringify(report, null, 2))
console.log('\nReport written to .tmp-listening-product-audit.json')
