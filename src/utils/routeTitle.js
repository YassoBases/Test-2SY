/** Resolve a translated page title from route meta. */
export function resolveRouteTitle(route, t) {
  if (route.meta?.titleKey) return t(route.meta.titleKey)
  if (route.meta?.title) return route.meta.title
  return ''
}
