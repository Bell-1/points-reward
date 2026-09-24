<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">🎯</div>
        <h1 class="login-title">积分奖励管理后台</h1>
        <p class="login-subtitle">家长管理端登录</p>
      </div>
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="form.username"
            type="text"
            class="form-input"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>
        <button
          type="submit"
          class="login-btn"
          :disabled="!form.username || !form.password || loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span>{{ loading ? '登录中...' : '登 录' }}</span>
        </button>
      </form>
      <div class="login-footer">
        <router-link to="/child/login" class="child-link">👶 孩子端登录 →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminLogin } from '../../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: 'admin',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  if (!form.username || !form.password) return
  loading.value = true
  try {
    const res = await adminLogin(form.username, form.password)
    authStore.setAuth(res.data)
    router.push('/admin/stats')
  } catch (e) {
    // error toast handled by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: #94a3b8;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.form-input {
  height: 44px;
  padding: 0 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  color: #1e293b;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #6366f1;
}

.login-btn {
  height: 46px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s, transform 0.1s;
  margin-top: 4px;
}

.login-btn:hover:not(:disabled) {
  opacity: 0.92;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.child-link {
  font-size: 14px;
  color: #6366f1;
  transition: color 0.2s;
}

.child-link:hover {
  color: #4f46e5;
}
</style>
