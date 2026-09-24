<template>
  <div class="child-layout">
    <header class="child-header">
      <div class="header-info">
        <span class="header-name">{{ authStore.nickname }}</span>
        <span class="header-points" @click="goRecords">
          <span class="points-icon">★</span>
          <span class="points-num">{{ balance }}</span>
        </span>
      </div>
      <button class="logout-btn" @click="handleLogout">退出</button>
    </header>

    <main class="child-main">
      <router-view />
    </main>

    <nav class="child-tabbar">
      <router-link to="/child/tasks" class="tab-item">
        <span class="tab-icon">✓</span>
        <span class="tab-text">任务</span>
      </router-link>
      <router-link to="/child/shop" class="tab-item">
        <span class="tab-icon">🛍</span>
        <span class="tab-text">商店</span>
      </router-link>
      <router-link to="/child/redemptions" class="tab-item">
        <span class="tab-icon">🎁</span>
        <span class="tab-text">兑换</span>
      </router-link>
      <router-link to="/child/records" class="tab-item">
        <span class="tab-icon">📋</span>
        <span class="tab-text">积分</span>
      </router-link>
      <router-link to="/child/progress" class="tab-item">
        <span class="tab-icon">📊</span>
        <span class="tab-text">进度</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getBalance } from '../api/child'

const router = useRouter()
const authStore = useAuthStore()
const balance = ref(0)

async function fetchBalance() {
  try {
    const res = await getBalance()
    balance.value = res.data.balance
  } catch (e) { /* ignore */ }
}

function goRecords() {
  router.push('/child/records')
}

function handleLogout() {
  authStore.logout()
  router.push('/child/login')
}

onMounted(() => {
  fetchBalance()
  window.addEventListener('balance-update', fetchBalance)
})
onUnmounted(() => {
  window.removeEventListener('balance-update', fetchBalance)
})
</script>

<style scoped>
.child-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #FFE5EC 0%, #E8F4FD 100%);
}

.child-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, #FF6B9D 0%, #C77DFF 100%);
  color: #fff;
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-name {
  font-size: 20px;
  font-weight: 700;
}

.header-points {
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}
.header-points:hover {
  background: rgba(255, 255, 255, 0.5);
}
.points-icon {
  color: #FFD700;
  margin-right: 4px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  transition: background 0.2s;
}
.logout-btn:hover {
  background: rgba(255, 255, 255, 0.4);
}

.child-main {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 80px;
}

.child-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 0 12px;
  color: #999;
  font-size: 12px;
  transition: color 0.2s;
}

.tab-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.tab-item.router-link-active {
  color: #FF6B9D;
}
</style>
