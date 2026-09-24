import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || null)
  const nickname = ref(localStorage.getItem('nickname') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isChild = computed(() => role.value === 'child')
  const isAdmin = computed(() => role.value === 'admin')

  function setAuth(data) {
    token.value = data.token
    role.value = data.role
    userId.value = data.userId
    nickname.value = data.nickname
    localStorage.setItem('token', data.token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('userId', data.userId)
    localStorage.setItem('nickname', data.nickname)
  }

  function logout() {
    token.value = ''
    role.value = ''
    userId.value = null
    nickname.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('userId')
    localStorage.removeItem('nickname')
  }

  return {
    token,
    role,
    userId,
    nickname,
    isLoggedIn,
    isChild,
    isAdmin,
    setAuth,
    logout,
  }
})
