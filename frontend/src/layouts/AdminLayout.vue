<template>
  <div class="admin-layout">
    <!-- Mobile header -->
    <header class="mobile-header">
      <button class="hamburger" @click="menuOpen = !menuOpen">
        <span class="hamburger-icon">{{ menuOpen ? '✕' : '☰' }}</span>
      </button>
      <div class="mobile-logo">
        <span class="logo-icon">🎯</span>
        <span class="logo-text">积分管理</span>
      </div>
      <div class="mobile-user">
        <span class="user-avatar">{{ authStore.nickname?.charAt(0) || 'A' }}</span>
      </div>
    </header>

    <!-- Mobile nav overlay -->
    <div v-if="menuOpen" class="nav-overlay" @click="menuOpen = false"></div>

    <!-- Sidebar -->
    <aside class="admin-sidebar" :class="{ 'sidebar-open': menuOpen }">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <span class="logo-icon">🎯</span>
          <span class="logo-text">积分管理</span>
        </div>
        <button class="close-btn" @click="menuOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/stats" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">📊</span>
          <span>数据统计</span>
        </router-link>
        <router-link to="/admin/tasks" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">📝</span>
          <span>任务管理</span>
        </router-link>
        <router-link to="/admin/reviews" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">🔍</span>
          <span>任务审核</span>
          <span v-if="pendingCount > 0" class="nav-badge">{{ pendingCount }}</span>
        </router-link>
        <router-link to="/admin/redemptions" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">🛒</span>
          <span>兑换审核</span>
          <span v-if="pendingRedemptionCount > 0" class="nav-badge">{{ pendingRedemptionCount }}</span>
        </router-link>
        <router-link to="/admin/products" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">🎁</span>
          <span>商品管理</span>
        </router-link>
        <router-link to="/admin/children" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">👶</span>
          <span>孩子管理</span>
        </router-link>
        <router-link to="/admin/points" class="nav-item" @click="menuOpen = false">
          <span class="nav-icon">💰</span>
          <span>积分管理</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-avatar">{{ authStore.nickname?.charAt(0) || 'A' }}</span>
          <span class="user-name">{{ authStore.nickname }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </aside>

    <!-- Desktop sidebar (hidden on mobile) -->
    <aside class="admin-sidebar-desktop">
      <div class="sidebar-logo">
        <span class="logo-icon">🎯</span>
        <span class="logo-text">积分管理</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/stats" class="nav-item">
          <span class="nav-icon">📊</span>
          <span>数据统计</span>
        </router-link>
        <router-link to="/admin/tasks" class="nav-item">
          <span class="nav-icon">📝</span>
          <span>任务管理</span>
        </router-link>
        <router-link to="/admin/reviews" class="nav-item">
          <span class="nav-icon">🔍</span>
          <span>任务审核</span>
          <span v-if="pendingCount > 0" class="nav-badge">{{ pendingCount }}</span>
        </router-link>
        <router-link to="/admin/redemptions" class="nav-item">
          <span class="nav-icon">🛒</span>
          <span>兑换审核</span>
          <span v-if="pendingRedemptionCount > 0" class="nav-badge">{{ pendingRedemptionCount }}</span>
        </router-link>
        <router-link to="/admin/products" class="nav-item">
          <span class="nav-icon">🎁</span>
          <span>商品管理</span>
        </router-link>
        <router-link to="/admin/children" class="nav-item">
          <span class="nav-icon">👶</span>
          <span>孩子管理</span>
        </router-link>
        <router-link to="/admin/points" class="nav-item">
          <span class="nav-icon">💰</span>
          <span>积分管理</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-avatar">{{ authStore.nickname?.charAt(0) || 'A' }}</span>
          <span class="user-name">{{ authStore.nickname }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </aside>

    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getPendingReviews, getPendingRedemptions } from '../api/admin'

const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)
const pendingCount = ref(0)
const pendingRedemptionCount = ref(0)

async function fetchPendingCount() {
  try {
    const res = await getPendingReviews()
    pendingCount.value = (res.data || []).filter((r) => r.status === 'pending').length
  } catch (e) { /* ignore */ }
}

async function fetchPendingRedemptionCount() {
  try {
    const res = await getPendingRedemptions()
    pendingRedemptionCount.value = (res.data || []).length
  } catch (e) { /* ignore */ }
}

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}

onMounted(() => {
  fetchPendingCount()
  fetchPendingRedemptionCount()
  window.addEventListener('reviews-updated', fetchPendingCount)
  window.addEventListener('redemptions-updated', fetchPendingRedemptionCount)
})
onUnmounted(() => {
  window.removeEventListener('reviews-updated', fetchPendingCount)
  window.removeEventListener('redemptions-updated', fetchPendingRedemptionCount)
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

/* ==================== Mobile Header ==================== */
.mobile-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #1e293b;
  z-index: 1001;
  align-items: center;
  padding: 0 12px;
  gap: 12px;
}

.hamburger {
  background: transparent;
  color: #fff;
  font-size: 24px;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.hamburger:hover {
  background: rgba(255, 255, 255, 0.1);
}

.mobile-logo {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.mobile-logo .logo-icon {
  font-size: 22px;
}

.mobile-user {
  display: flex;
  align-items: center;
}

.mobile-user .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
}

/* ==================== Nav Overlay ==================== */
.nav-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1002;
}

/* ==================== Mobile Sidebar ==================== */
.admin-sidebar {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  background: #1e293b;
  z-index: 1003;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.admin-sidebar.sidebar-open {
  transform: translateX(0);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header .sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  color: #94a3b8;
  font-size: 20px;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* ==================== Desktop Sidebar ==================== */
.admin-sidebar-desktop {
  width: 220px;
  background: #1e293b;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 26px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #94a3b8;
  font-size: 15px;
  transition: all 0.2s;
  text-decoration: none;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.nav-item.router-link-active {
  background: rgba(99, 102, 241, 0.2);
  color: #fff;
  border-left: 3px solid #6366f1;
}

.nav-icon {
  font-size: 20px;
}

.nav-badge {
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 10px;
  margin-left: auto;
  min-width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
}

.user-name {
  color: #e2e8f0;
  font-size: 14px;
}

.logout-btn {
  width: 100%;
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  padding: 8px;
  border-radius: 6px;
  font-size: 14px;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* ==================== Main Content ==================== */
.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* ==================== Responsive: Mobile ==================== */
@media (max-width: 768px) {
  .mobile-header {
    display: flex;
  }

  .nav-overlay {
    display: block;
  }

  .admin-sidebar {
    display: flex;
  }

  .admin-sidebar-desktop {
    display: none;
  }

  .admin-main {
    padding: 16px;
    padding-top: 72px;
  }
}
</style>
