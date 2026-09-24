<template>
  <div class="toast-container" v-if="messages.length">
    <div class="toast-msg" v-for="msg in messages" :key="msg.id">{{ msg.text }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const messages = ref([])
let idCounter = 0

function onToast(event) {
  const id = ++idCounter
  messages.value.push({ id, text: event.detail })
  setTimeout(() => {
    messages.value = messages.value.filter((m) => m.id !== id)
  }, 2500)
}

onMounted(() => window.addEventListener('toast', onToast))
onUnmounted(() => window.removeEventListener('toast', onToast))
</script>
