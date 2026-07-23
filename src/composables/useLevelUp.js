// Detects a CEFR level-up across loads by remembering the last-seen overall level, and exposes
// shared reactive state for the LevelUpCelebration modal. Any view that knows the current level
// calls checkLevelUp(level); the first one to see an increase triggers the celebration.
import { reactive } from 'vue'

const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const KEY = 'lang_last_overall_level'

export const levelUpState = reactive({ show: false, from: '', to: '' })

function isLevel(level) {
  return Boolean(level && CEFR.includes(level))
}

function levelRank(level) {
  return CEFR.indexOf(level)
}

function readSeenLevel() {
  let prev = null
  try {
    prev = localStorage.getItem(KEY)
  } catch {
    /* storage unavailable */
  }
  return isLevel(prev) ? prev : null
}

function writeSeenLevel(level) {
  try {
    localStorage.setItem(KEY, level)
  } catch {
    /* storage unavailable */
  }
}

export function syncLevelSeen(currentLevel, { allowLower = false } = {}) {
  if (!isLevel(currentLevel)) return
  const prev = readSeenLevel()
  if (!prev || allowLower || levelRank(currentLevel) >= levelRank(prev)) {
    writeSeenLevel(currentLevel)
  }
}

export function checkLevelUp(currentLevel) {
  if (!isLevel(currentLevel)) return
  const prev = readSeenLevel()
  if (prev && levelRank(currentLevel) > levelRank(prev)) {
    levelUpState.from = prev
    levelUpState.to = currentLevel
    levelUpState.show = true
  }
  syncLevelSeen(currentLevel)
}

export function dismissLevelUp() {
  levelUpState.show = false
}
