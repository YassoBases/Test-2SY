import { mediaUrl } from './media.js'

/** Resolve teacher profile image path to an absolute URL. */
export function resolveTeacherAvatarUrl(url) {
  if (!url) return null
  return mediaUrl(url)
}

/**
 * Avatar URL for a conversation participant.
 * Uses per-participant avatar_url from the API only.
 * Optional fallback applies ONLY when the participant is the logged-in teacher (self).
 *
 * @param {object|null} participant - { user_id, avatar_url, role, ... }
 * @param {string|null} [selfAvatarUrl] - logged-in teacher's own avatar
 * @param {number|null} [viewerUserId] - current user id
 */
export function participantAvatarUrl(participant, selfAvatarUrl = null, viewerUserId = null) {
  if (!participant) return null
  if (participant.avatar_url) return participant.avatar_url
  const isSelf =
    participant.role === 'teacher' &&
    viewerUserId != null &&
    participant.user_id === viewerUserId &&
    selfAvatarUrl
  return isSelf ? selfAvatarUrl : null
}

/** Display name: profile display_name / full_name / name, else fallback. */
export function teacherDisplayName(entity, fallback = '') {
  if (!entity) return fallback
  return (
    entity.display_name ||
    entity.full_name ||
    entity.teacher_name ||
    entity.name ||
    fallback
  )
}

/** Pick image from common API field names. */
export function teacherImageFromEntity(entity) {
  if (!entity) return null
  return (
    entity.avatar_url ||
    entity.image_url ||
    entity.teacher_image_url ||
    null
  )
}
