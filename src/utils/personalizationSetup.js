import { getSession, setSession } from './session.js'

export function isPersonalizationSetupComplete() {
  return !!getSession()?.personalizationSetupComplete
}

export function markPersonalizationSetupComplete() {
  const session = getSession()
  if (!session) return
  setSession({ ...session, personalizationSetupComplete: true })
}
