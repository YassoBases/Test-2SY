/** Eager-load all locale JSON modules into vue-i18n message trees. */
const modules = import.meta.glob('../locales/*/*.json', { eager: true })

export function buildMessages() {
  const messages = { ar: {}, en: {} }

  for (const path of Object.keys(modules)) {
    const match = path.match(/locales\/(ar|en)\/([^/]+)\.json$/)
    if (!match) continue
    const [, locale, namespace] = match
    messages[locale][namespace] = modules[path].default
  }

  return messages
}
