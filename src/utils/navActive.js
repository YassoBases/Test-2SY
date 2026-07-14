/**
 * Sidebar active-state rules (exactly one item at a time).
 * - Hash links: active only when path + hash both match.
 * - Plain paths: active on exact path with no hash; optional matchChildren for nested routes.
 */

export function parseNavTarget(to) {
  const raw = String(to || '')
  const hashIdx = raw.indexOf('#')
  if (hashIdx === -1) {
    return { path: raw, hash: '' }
  }
  return {
    path: raw.slice(0, hashIdx),
    hash: `#${raw.slice(hashIdx + 1)}`,
  }
}

/**
 * @param {import('vue-router').RouteLocationNormalizedLoaded} route
 * @param {{ to: string, matchChildren?: boolean }} item
 */
export function isNavItemActive(route, item) {
  const target = parseNavTarget(item.to)
  const path = route.path
  const hash = route.hash || ''

  if (target.hash) {
    return path === target.path && hash === target.hash
  }

  if (path === target.path) {
    return !hash
  }

  if (item.matchChildren && path.startsWith(`${target.path}/`)) {
    return true
  }

  return false
}

export function navItemKey(item) {
  return `${item.to}::${item.title}`
}
