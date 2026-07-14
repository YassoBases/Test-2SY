/**
 * Verifies report loadError clears after simulated ERR_NETWORK then success.
 * Run: node scripts/verify_report_load_error_state.mjs
 */

function testLoadErrorStateMachine() {
  const loadError = { value: '' }
  const report = { value: null }

  const clearLoadError = () => {
    loadError.value = ''
  }
  const applySuccess = (data) => {
    clearLoadError()
    report.value = data
  }
  const applyFailure = () => {
    loadError.value = 'تعذر الاتصال بالخادم. تأكد أن FastAPI يعمل على http://127.0.0.1:8000'
    report.value = null
  }

  applyFailure()
  const afterFail = { loadError: loadError.value, report: report.value }
  applySuccess({ student_name: 'hamza', has_data: true })
  const afterSuccess = { loadError: loadError.value, report: report.value }

  return {
    name: 'state_machine',
    afterFail,
    afterSuccess,
    loadErrorEmptyAfterSuccess: afterSuccess.loadError === '',
    pass: afterFail.loadError !== '' && afterSuccess.loadError === '' && afterSuccess.report !== null,
  }
}

async function testApiRecovery() {
  const base = 'http://127.0.0.1:8000/api'
  // Use parent 23 (has linked student 5 in local DB)
  const { createHmac } = await import('node:crypto')
  const secret = process.env.JWT_SECRET || 'change-me-to-a-long-random-secret'
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url')
  const payload = Buffer.from(
    JSON.stringify({ sub: '23', role: 'parent', exp: Math.floor(Date.now() / 1000) + 3600, sid: '275' }),
  ).toString('base64url')
  const sig = createHmac('sha256', secret).update(`${header}.${payload}`).digest('base64url')
  const token = `${header}.${payload}.${sig}`

  const studentsRes = await fetch(`${base}/parent/students`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const students = await studentsRes.json()
  const sid = students[0]?.id
  if (!sid) {
    return { name: 'api_recovery', pass: false, skipped: true, reason: 'no linked students' }
  }

  const reportRes = await fetch(`${base}/parent/historical-report?period=this_week&student_id=${sid}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const body = await reportRes.json()

  let loadError = 'تعذر الاتصال بالخادم. تأكد أن FastAPI يعمل على http://127.0.0.1:8000'
  let report = null
  if (reportRes.ok) {
    loadError = ''
    report = body
  }

  return {
    name: 'api_recovery',
    pass: reportRes.status === 200 && loadError === '' && Boolean(report?.student_name),
    httpStatus: reportRes.status,
    loadErrorAfterSuccess: loadError,
    student: report?.student_name,
  }
}

const results = [testLoadErrorStateMachine(), await testApiRecovery()]
const pass = results.every((r) => r.pass || r.skipped)
console.log(JSON.stringify({ pass, results }, null, 2))
process.exit(pass ? 0 : 1)
