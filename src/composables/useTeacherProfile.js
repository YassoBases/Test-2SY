import { ref } from 'vue'
import { fetchTeacherSetupStatus } from '../api/teacherSetup.js'

const teacherProfile = ref({
  full_name: '',
  image_url: null,
  bio: null,
})
let loaded = false

export function refreshTeacherProfileCache(status) {
  if (!status) return
  const avatar = status.avatar_url || status.image_url || null
  teacherProfile.value = {
    full_name: status.display_name || status.full_name || '',
    image_url: avatar,
    bio: status.bio || null,
  }
  loaded = true
}

export function invalidateTeacherProfileCache() {
  loaded = false
  teacherProfile.value = {
    full_name: '',
    image_url: null,
    bio: null,
  }
}

export async function ensureTeacherProfile() {
  if (loaded) return teacherProfile.value
  try {
    const status = await fetchTeacherSetupStatus()
    refreshTeacherProfileCache(status)
  } catch {
    /* ignore — header falls back to initials */
  }
  return teacherProfile.value
}

export function useTeacherProfile() {
  return {
    teacherProfile,
    ensureTeacherProfile,
    refreshTeacherProfileCache,
    invalidateTeacherProfileCache,
  }
}
