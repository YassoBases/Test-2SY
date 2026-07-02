/** Partition planner schedule slots for dashboard sections. */

function startOfDay(d) {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x
}

function endOfWeek(d) {
  const x = startOfDay(d)
  const day = x.getDay()
  const diff = day === 0 ? 0 : 7 - day
  x.setDate(x.getDate() + diff)
  x.setHours(23, 59, 59, 999)
  return x
}

export function isToday(iso) {
  const d = new Date(iso)
  const now = new Date()
  return startOfDay(d).getTime() === startOfDay(now).getTime()
}

export function isThisWeek(iso) {
  const d = new Date(iso)
  const now = new Date()
  return d >= startOfDay(now) && d <= endOfWeek(now)
}

export function partitionSchedule(schedule = []) {
  const today = []
  const thisWeek = []
  const later = []
  const now = new Date()

  for (const slot of schedule) {
    if (!slot?.scheduled_at) continue
    const at = new Date(slot.scheduled_at)
    if (at < now && slot.status !== 'planned') continue
    if (isToday(slot.scheduled_at)) {
      today.push(slot)
    } else if (isThisWeek(slot.scheduled_at)) {
      thisWeek.push(slot)
    } else if (at >= now) {
      later.push(slot)
    }
  }

  const byTime = (a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at)
  today.sort(byTime)
  thisWeek.sort(byTime)
  later.sort(byTime)

  return { today, thisWeek, later }
}

export function upcomingDeadlines(lifeEvents = [], schedule = []) {
  const items = []
  for (const ev of lifeEvents) {
    if (ev.event_type === 'exam') {
      items.push({
        id: `ev-${ev.id}`,
        title: ev.title || 'امتحان',
        subtitle: ev.subject || 'موعد امتحان',
        icon: 'mdi-file-document-alert',
        color: 'error',
      })
    }
  }
  for (const slot of schedule) {
    if (slot.status === 'planned' && slot.priority >= 4) {
      items.push({
        id: `slot-${slot.id}`,
        title: slot.subject,
        subtitle: slot.reasoning || 'جلسة ذات أولوية',
        icon: 'mdi-flag',
        color: 'warning',
        at: slot.scheduled_at,
      })
    }
  }
  return items.slice(0, 8)
}
