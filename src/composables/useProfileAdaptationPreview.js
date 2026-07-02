import { computed, unref } from 'vue'
import {
  learningStyleIdentityOptions,
  personalityIdentityOptions,
  interestOptions,
  hobbyOptions,
  ageBandLabel,
  goalIdentityTitle,
} from '../data/profileOptions.js'

function interestLabel(value) {
  return (
    interestOptions.find((o) => o.value === value)?.title
    || hobbyOptions.find((o) => o.value === value)?.title
  )
}

function personalityLabel(value) {
  return personalityIdentityOptions.find((o) => o.value === value)?.title
}

/** Human-readable bullets from profile prefs — no internal AI labels. */
export function useProfileAdaptationPreview(prefsSource) {
  return computed(() => {
    const prefs = unref(prefsSource)
    const bullets = []

    switch (prefs.learning_style) {
      case 'practical':
        bullets.push('سأستخدم أمثلة عملية لتوضيح المفاهيم')
        break
      case 'visual':
        bullets.push('سأشرح بالأمثلة والتصوّر لتسهيل الفهم')
        break
      case 'step_by_step':
        bullets.push('سأقسّم كل فكرة إلى خطوات واضحة')
        break
      case 'theoretical':
        bullets.push('سأبدأ بالمفاهيم الأساسية ثم أربطها بالأمثلة')
        break
      default:
        break
    }

    if (ageBandLabel(prefs.age)) {
      bullets.push('سأشرح بمستوى مناسب لفئتك العمرية')
    }

    const personality = personalityLabel(prefs.personality_mode)
    if (personality) {
      bullets.push(`سأستخدم أسلوب ${personality} أثناء الشرح`)
    }

    switch (prefs.preferred_explanation_style) {
      case 'short':
        bullets.push('سأجيب بشكل مختصر ومركّز')
        break
      case 'detailed':
        bullets.push('سأشرح بتفصيل أكبر عندما تحتاج')
        break
      default:
        bullets.push('سأوازن بين التبسيط والتفصيل')
        break
    }

    switch (prefs.difficulty) {
      case 'easy':
        bullets.push('سأبني الشرح بوتيرة هادئة مع أمثلة إضافية')
        break
      case 'hard':
        bullets.push('سأقدّم تحديات أعمق عندما تكون جاهزاً')
        break
      default:
        break
    }

    const topicLabels = [...(prefs.interests || []), ...(prefs.hobbies || [])]
      .map(interestLabel)
      .filter(Boolean)
      .slice(0, 2)

    if (topicLabels.length === 1) {
      bullets.push(`سأربط بعض الأمثلة بـ${topicLabels[0]}`)
    } else if (topicLabels.length >= 2) {
      bullets.push(`سأربط بعض الأمثلة بـ${topicLabels[0]} و${topicLabels[1]}`)
    }

    const goalTitle = goalIdentityTitle(prefs.future_goal)
    if (goalTitle && prefs.future_goal !== 'undecided') {
      bullets.push(`سأربط ما تتعلّمه بطموحك: ${goalTitle}`)
    }

    return [...new Set(bullets)].slice(0, 5)
  })
}
