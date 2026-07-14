/** Normalize Vuetify v-file-input model (File | File[] | null). */
export function pickFirstFile(value) {
  if (!value) return null
  if (Array.isArray(value)) return value[0] || null
  if (value instanceof File) return value
  return null
}
