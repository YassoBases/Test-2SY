// Detects a CEFR level-up across loads by remembering the last-seen overall level, and exposes
// shared reactive state for the LevelUpCelebration modal. Any view that knows the current level
// calls checkLevelUp(level); the first one to see an increase triggers the celebration.
import { reactive } from 'vue'

const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const KEY = 'lang_last_overall_level'

export const levelUpState = reactive({ show: false, from: '', to: '' })

export function checkLevelUp(currentLevel) {
  if (!currentLevel || !CEFR.includes(currentLevel)) return
  let prev = null
  try {
    prev = localStorage.getItem(KEY)
  } catch {
    /* storage unavailable */
  }
  if (prev && CEFR.indexOf(currentLevel) > CEFR.indexOf(prev)) {
    levelUpState.from = prev
    levelUpState.to = currentLevel
    levelUpState.show = true
  }
  try {
    localStorage.setItem(KEY, currentLevel)
  } catch {
    /* storage unavailable */
  }
}

export function dismissLevelUp() {
  levelUpState.show = false
}
