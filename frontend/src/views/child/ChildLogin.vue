<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">🌟</div>
      <h1 class="login-title">积分小达人</h1>
      <p class="login-subtitle">完成任务，赚取积分，兑换好礼！</p>

      <div class="form-group">
        <label class="form-label">选择账号</label>
        <select v-model="selectedChildId" class="form-select" :disabled="loadingChildren">
          <option value="" disabled>{{ loadingChildren ? '加载中...' : '请选择宝贝' }}</option>
          <option v-for="child in childrenList" :key="child.id" :value="child.id">
            {{ child.nickname }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">PIN 码</label>
        <input
          v-model="pin"
          type="password"
          class="form-input"
          placeholder="请输入 4-8 位数字 PIN 码"
          maxlength="8"
          inputmode="numeric"
          @keyup.enter="handleLogin"
        />
      </div>

      <button
        class="login-btn"
        :disabled="!canLogin || loggingIn"
        @click="handleLogin"
      >
        {{ loggingIn ? '登录中...' : '登录 ✨' }}
      </button>

      <button class="admin-link" @click="goAdminLogin">家长入口 →</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { childLogin, getChildrenList } from '../../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const childrenList = ref([])
const selectedChildId = ref('')
const pin = ref('')
const loadingChildren = ref(true)
const loggingIn = ref(false)

const canLogin = computed(() => selectedChildId.value !== '' && pin.value !== '')

async function fetchChildren() {
  loadingChildren.value = true
  try {
    const res = await getChildrenList()
    childrenList.value = res.data
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loadingChildren.value = false
  }
}

async function handleLogin() {
  if (!canLogin.value) return
  loggingIn.value = true
  try {
    const res = await childLogin(Number(selectedChildId.value), pin.value)
    authStore.setAuth(res.data)
    router.push('/child/tasks')
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loggingIn.value = false
  }
}

function goAdminLogin() {
  router.push('/admin/login')
}

onMounted(fetchChildren)
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #FF6B9D 0%, #C77DFF 50%, #7B68EE 100%);
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 28px;
  padding: 40px 32px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.login-logo {
  font-size: 56px;
  line-height: 1;
  margin-bottom: 12px;
}

.login-title {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #999;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.form-select,
.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #eee;
  border-radius: 16px;
  font-size: 17px;
  transition: border-color 0.2s;
  background: #fafafa;
}

.form-select:focus,
.form-input:focus {
  border-color: #C77DFF;
  background: #fff;
}

.form-select:disabled {
  opacity: 0.6;
}

.login-btn {
  width: 100%;
  padding: 16px;
  margin-top: 8px;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 8px 24px rgba(255, 107, 157, 0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}

.login-btn:not(:disabled):active {
  transform: scale(0.97);
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.35);
}

.login-btn:disabled {
  opacity: 0.5;
  box-shadow: none;
}

.admin-link {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 10px;
  font-size: 14px;
  color: #aaa;
  background: transparent;
  transition: color 0.2s;
}

.admin-link:hover {
  color: #C77DFF;
}
</style>
