export const FEATURE_META = {
  conversation: { icon: 'mdi-robot-happy-outline', color: 'secondary', label: 'محادثة' },
  speaking: { icon: 'mdi-microphone', color: 'secondary', label: 'تحدث' },
  reading: { icon: 'mdi-book-open-variant', color: 'primary', label: 'قراءة' },
  listening: { icon: 'mdi-headphones', color: 'primary', label: 'استماع' },
  writing: { icon: 'mdi-pencil', color: 'primary', label: 'كتابة' },
  vocabulary: { icon: 'mdi-cards-outline', color: 'primary', label: 'مفردات' },
}

export const STATUS_META = {
  new: { label: 'قادم', color: 'medium-emphasis', icon: 'mdi-circle-outline' },
  in_progress: { label: 'الهدف الحالي', color: 'info', icon: 'mdi-progress-clock' },
  mastered: { label: 'متقن', color: 'success', icon: 'mdi-check-circle' },
}

export function featureIcon(f) {
  return (FEATURE_META[f] || FEATURE_META.conversation).icon
}

export function featureColor(f) {
  return (FEATURE_META[f] || FEATURE_META.conversation).color
}

export function featureLabel(f) {
  return (FEATURE_META[f] || FEATURE_META.conversation).label
}

export function statusMeta(status) {
  return STATUS_META[status] || STATUS_META.new
}

/** @returns {'completed'|'current'|'upcoming'} */
export function objectiveNodeState(objective, index, objectives) {
  if (objective.status === 'mastered') return 'completed'
  const firstIncomplete = objectives.findIndex((o) => o.status !== 'mastered')
  if (firstIncomplete === -1) return 'completed'
  if (index === firstIncomplete) return 'current'
  if (index > firstIncomplete) return 'upcoming'
  return 'completed'
}

export function currentObjectivePosition(objectives) {
  const total = objectives?.length || 0
  if (!total) return { index: 0, total: 0, label: null }
  const firstIncomplete = objectives.findIndex((o) => o.status !== 'mastered')
  if (firstIncomplete === -1) {
    return { index: total, total, label: `الهدف ${total} من ${total}` }
  }
  return {
    index: firstIncomplete + 1,
    total,
    label: `الهدف ${firstIncomplete + 1} من ${total}`,
  }
}
