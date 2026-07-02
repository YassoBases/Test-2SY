/** Messaging UI helpers (frontend only). */

export const ROLE_LABELS = { teacher: 'معلّم', student: 'طالب', parent: 'ولي أمر' }

export const ROLE_ICONS = {
  teacher: 'mdi-account-tie',
  student: 'mdi-account-school',
  parent: 'mdi-account-supervisor-circle',
}

/**
 * Whether the message was sent by the logged-in user.
 * Prefer sender_id === viewerId (source of truth); fall back to API is_mine.
 */
export function resolveIsMine(msg, viewerId) {
  if (msg == null) return false
  const senderId = msg.sender_id ?? msg.senderId
  if (viewerId != null && viewerId !== '' && senderId != null && senderId !== '') {
    return Number(senderId) === Number(viewerId)
  }
  const flag = msg.is_mine ?? msg.isMine
  if (typeof flag === 'boolean') return flag
  if (flag === 1 || flag === '1' || flag === 'true') return true
  return false
}

/** Physical screen sides (LTR flex on row): mine = right, others = left. */
export function messageAlignClass(isMine) {
  return isMine ? 'msg-row--mine' : 'msg-row--other'
}

export function bubbleVariantClass(role) {
  if (role === 'teacher') return 'msg-bubble--teacher'
  if (role === 'parent') return 'msg-bubble--parent'
  return 'msg-bubble--student'
}

export function roleChipColor(role) {
  const map = { teacher: 'primary', student: 'cyan', parent: 'secondary' }
  return map[role] || 'default'
}

export function primaryOtherParticipant(conv, viewerId) {
  if (!conv) return null
  const list = conv.other_participants?.length
    ? conv.other_participants
    : (conv.participants || []).filter((p) => p.user_id !== viewerId)
  if (!list.length) return null
  const teacher = list.find((p) => p.role === 'teacher')
  return teacher || list[0]
}

export function formatListTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const now = new Date()
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const startOfYesterday = new Date(startOfToday)
    startOfYesterday.setDate(startOfYesterday.getDate() - 1)

    if (d >= startOfToday) {
      return new Intl.DateTimeFormat('ar-SY', { hour: 'numeric', minute: '2-digit', hour12: true }).format(d)
    }
    if (d >= startOfYesterday) {
      return 'أمس'
    }
    return new Intl.DateTimeFormat('ar-SY', { day: 'numeric', month: 'short' }).format(d)
  } catch {
    return iso
  }
}

export function formatMessageTime(iso) {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('ar-SY', { hour: 'numeric', minute: '2-digit', hour12: true }).format(new Date(iso))
  } catch {
    return iso
  }
}

/** Optional presence line from participant fields when API provides them. */
export function formatPresenceStatus(participant) {
  if (!participant) return null
  if (participant.is_online === true || participant.online === true) {
    return { text: 'متصل الآن', online: true }
  }
  const last =
    participant.last_active_at ||
    participant.last_seen_at ||
    participant.last_active ||
    participant.last_active_date
  if (!last) return null
  try {
    const d = new Date(last)
    const now = new Date()
    const diffMs = now - d
    const diffMin = Math.floor(diffMs / 60000)
    if (diffMin < 5) return { text: 'متصل مؤخراً', online: true }
    if (diffMin < 60) return { text: `آخر ظهور منذ ${diffMin} د`, online: false }
    const diffHr = Math.floor(diffMin / 60)
    if (diffHr < 24) return { text: `آخر ظهور منذ ${diffHr} س`, online: false }
    return { text: `آخر ظهور ${formatListTime(last)}`, online: false }
  } catch {
    return { text: `آخر ظهور ${last}`, online: false }
  }
}

export function statusMeta(status) {
  const map = {
    sent: { icon: 'mdi-check', label: 'أُرسلت', color: 'muted' },
    delivered: { icon: 'mdi-check-all', label: 'وُصلت', color: 'muted' },
    read: { icon: 'mdi-check-all', label: 'قُرئت', color: 'read' },
  }
  return map[status] || map.sent
}

export function findTeacherParentThread(conversations, studentId, parentUserId) {
  if (!studentId || !parentUserId || !Array.isArray(conversations)) return null
  return (
    conversations.find(
      (c) =>
        c.student_id === studentId &&
        c.thread_type === 'teacher_parent' &&
        (c.participants || []).some((p) => p.role === 'parent' && p.user_id === parentUserId),
    ) || null
  )
}

export function parentParticipantFromThread(thread, parentUserId) {
  return (thread?.participants || []).find((p) => p.role === 'parent' && p.user_id === parentUserId) || null
}

export function buildLinkedParentsMenuItems(linkedParents, studentId, conversations) {
  return (linkedParents || []).map((p) => {
    const thread = findTeacherParentThread(conversations, studentId, p.parent_id)
    const participant = parentParticipantFromThread(thread, p.parent_id)
    return {
      parent_id: p.parent_id,
      full_name: p.full_name,
      relationship_label: p.relationship_label,
      email: p.email,
      threadId: thread?.id ?? null,
      presence: formatPresenceStatus(participant),
    }
  })
}

export function cacheParentRelationships(cache, studentId, linkedParents) {
  if (!studentId || !linkedParents?.length) return cache || {}
  const next = { ...(cache || {}) }
  for (const p of linkedParents) {
    if (p.parent_id) next[`${p.parent_id}-${studentId}`] = p.relationship_label
  }
  return next
}

export function parentRelationshipFromCache(cache, parentUserId, studentId) {
  if (!cache || parentUserId == null || studentId == null) return null
  return cache[`${parentUserId}-${studentId}`] || null
}
