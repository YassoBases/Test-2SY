<template>

  <div class="typing-row d-flex align-end gap-2 chat-row">

    <LessonChatTeacherAvatar

      :name="teacherName"

      :image-url="teacherImageUrl"

      :size="34"

    />

    <div class="typing-bubble rounded-lg d-flex align-center">

      <div class="typing-dots d-flex align-center gap-1">

        <span v-for="i in 3" :key="i" class="typing-dot" :style="{ animationDelay: `${i * 0.15}s` }" />

      </div>

    </div>

  </div>

</template>



<script setup>

import LessonChatTeacherAvatar from './LessonChatTeacherAvatar.vue'



defineProps({

  teacherName: { type: String, default: '' },

  teacherImageUrl: { type: String, default: null },

})

</script>



<style scoped>

.typing-dot {

  width: 6px;

  height: 6px;

  border-radius: 50%;

  background: var(--em-cyan);

  animation: typing-bounce 1s ease-in-out infinite;

}



@keyframes typing-bounce {

  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }

  30% { transform: translateY(-3px); opacity: 1; }

}

</style>

