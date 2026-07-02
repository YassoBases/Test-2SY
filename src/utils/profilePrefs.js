import { defaultProfilePrefs } from '../data/profileOptions.js'

export function buildProfilePayload(prefs) {
  return {
    interests: [...(prefs.interests || [])],
    hobbies: [...(prefs.hobbies || [])],
    difficulty: prefs.difficulty || defaultProfilePrefs.difficulty,
    age: prefs.age || null,
    learning_style: prefs.learning_style || defaultProfilePrefs.learning_style,
    future_goal: prefs.future_goal || defaultProfilePrefs.future_goal,
    preferred_explanation_style:
      prefs.preferred_explanation_style || defaultProfilePrefs.preferred_explanation_style,
    personality_mode: prefs.personality_mode || defaultProfilePrefs.personality_mode,
  }
}

export function applyProfileData(prefs, data) {
  if (!data) return
  prefs.interests = [...(data.interests || defaultProfilePrefs.interests)]
  prefs.hobbies = [...(data.hobbies || [])]
  prefs.difficulty = data.difficulty || defaultProfilePrefs.difficulty
  prefs.age = data.age ?? null
  prefs.learning_style = data.learning_style || defaultProfilePrefs.learning_style
  prefs.future_goal = data.future_goal || defaultProfilePrefs.future_goal
  prefs.preferred_explanation_style =
    data.preferred_explanation_style || defaultProfilePrefs.preferred_explanation_style
  prefs.personality_mode = data.personality_mode || defaultProfilePrefs.personality_mode
}

export function createDefaultProfilePrefs() {
  return {
    interests: [...defaultProfilePrefs.interests],
    hobbies: [...defaultProfilePrefs.hobbies],
    difficulty: defaultProfilePrefs.difficulty,
    age: defaultProfilePrefs.age,
    learning_style: defaultProfilePrefs.learning_style,
    future_goal: defaultProfilePrefs.future_goal,
    preferred_explanation_style: defaultProfilePrefs.preferred_explanation_style,
    personality_mode: defaultProfilePrefs.personality_mode,
  }
}
