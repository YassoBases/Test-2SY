<template>
  <div v-if="participants.length" class="participant-bar">
    <div class="participant-bar__scroll chat-scroll">
      <div v-for="p in participants" :key="p.user_id" class="participant-pill">
        <ParticipantAvatar
          :name="p.display_name || p.name"
          :role="p.role"
          :image-url="participantAvatarUrl(p, teacherAvatarUrl, viewerId)"
          :size="28"
          :show-role-badge="false"
        />
        <span class="participant-pill__name text-truncate">{{ p.display_name || p.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import ParticipantAvatar from './ParticipantAvatar.vue'
import { participantAvatarUrl } from '../../utils/teacherAvatar.js'

defineProps({
  participants: { type: Array, default: () => [] },
  teacherAvatarUrl: { type: String, default: null },
  viewerId: { type: Number, default: null },
})
</script>

<style scoped>
.participant-bar {
  background: rgba(17, 24, 39, 0.6);
}
.participant-bar__scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 6px 12px;
}
.participant-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  padding: 4px 10px 4px 4px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  max-width: 160px;
}
.participant-pill__name {
  font-size: 0.72rem;
  font-weight: 600;
  color: #e2e8f0;
}
</style>
