<template>
  <div class="progress-page">
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-btn"
        :class="{ active: activeTab === tab.value }"
        @click="switchTab(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="loading-emoji">⏳</span>
      <p>加载中...</p>
    </div>

    <template v-else-if="progressData">
      <!-- Circular Progress Ring -->
      <div class="ring-section">
        <svg class="progress-ring" width="160" height="160" viewBox="0 0 160 160">
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#FF6B9D" />
              <stop offset="100%" stop-color="#C77DFF" />
            </linearGradient>
          </defs>
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="#FFE5EC"
            stroke-width="12"
          />
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="url(#progressGradient)"
            stroke-width="12"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            transform="rotate(-90 80 80)"
            class="progress-ring-fill"
          />
        </svg>
        <div class="ring-center">
          <span class="ring-percent">{{ displayPercent }}%</span>
          <span class="ring-label">完成率</span>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-num">{{ progressData.completedCount }}</span>
          <span class="stat-label">已完成</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ progressData.totalCount }}</span>
          <span class="stat-label">总任务</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ displayPercent }}%</span>
          <span class="stat-label">完成率</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-bar-section">
        <div class="progress-bar-track">
          <div class="progress-bar-fill" :style="{ width: displayPercent + '%' }"></div>
        </div>
      </div>

      <!-- Task List -->
      <div v-if="progressData.tasks.length === 0" class="empty-state">
        <span class="empty-emoji">🎈</span>
        <p>暂无任务</p>
      </div>
      <div v-else class="task-list">
        <div
          v-for="task in progressData.tasks"
          :key="task.id"
          class="task-item"
          :class="{
            'status-approved': task.completionStatus === 'approved',
            'status-pending': task.completionStatus === 'pending',
            'status-rejected': task.completionStatus === 'rejected',
          }"
        >
          <span class="task-status-icon">
            {{ statusIcon(task.completionStatus) }}
          </span>
          <span class="task-icon">{{ task.icon || '⭐' }}</span>
          <div class="task-info">
            <span class="task-name">{{ task.taskName }}</span>
            <span class="task-reward">★ {{ task.rewardPoints }}</span>
          </div>
          <span class="task-badge" :class="badgeClass(task.completionStatus)">
            {{ statusLabel(task.completionStatus) }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTaskProgress } from '../../api/child'

const tabs = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' },
]

const activeTab = ref('daily')
const progressData = ref(null)
const loading = ref(false)

const radius = 70
const circumference = 2 * Math.PI * radius

function statusIcon(status) {
  return { approved: '✅', pending: '🕐', rejected: '❌' }[status] || '⭕'
}

function statusLabel(status) {
  return { approved: '已通过', pending: '待验证', rejected: '已驳回' }[status] || '待完成'
}

function badgeClass(status) {
  return { approved: 'badge-done', pending: 'badge-pending', rejected: 'badge-rejected' }[status] || 'badge-todo'
}

const displayPercent = computed(() => {
  const rate = progressData.value?.completionRate ?? 0
  return rate > 1 ? Math.round(rate) : Math.round(rate * 100)
})

const dashOffset = computed(() => {
  return circumference * (1 - displayPercent.value / 100)
})

async function fetchProgress() {
  loading.value = true
  try {
    const res = await getTaskProgress(activeTab.value)
    progressData.value = res.data
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loading.value = false
  }
}

function switchTab(tabValue) {
  if (activeTab.value === tabValue) return
  activeTab.value = tabValue
  fetchProgress()
}

onMounted(fetchProgress)
</script>

<style scoped>
.progress-page {
  padding: 16px;
}

.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #999;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.tab-btn.active {
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 16px rgba(199, 125, 255, 0.35);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.loading-emoji,
.empty-emoji {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

/* Circular Progress Ring */
.ring-section {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 24px;
}

.progress-ring {
  display: block;
}

.progress-ring-fill {
  transition: stroke-dashoffset 0.6s ease;
}

.ring-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ring-percent {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.ring-label {
  font-size: 13px;
  color: #aaa;
  margin-top: 2px;
}

/* Stats */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-num {
  font-size: 24px;
  font-weight: 800;
  color: #C77DFF;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

/* Progress Bar */
.progress-bar-section {
  margin-bottom: 24px;
}

.progress-bar-track {
  width: 100%;
  height: 16px;
  border-radius: 8px;
  background: #FFE5EC;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(90deg, #FF6B9D, #C77DFF);
  transition: width 0.6s ease;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s;
}

.task-item:hover {
  transform: translateX(2px);
}

.task-item.status-approved {
  background: linear-gradient(135deg, #F0FFF4 0%, #E6FFFA 100%);
}

.task-item.status-pending {
  background: linear-gradient(135deg, #FFFEF0 0%, #FEF3C7 100%);
}

.task-item.status-rejected {
  background: linear-gradient(135deg, #FFF0F0 0%, #FED7D7 100%);
}

.task-status-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.task-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FFF0F5, #F3E8FF);
}

.task-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-reward {
  font-size: 14px;
  font-weight: 700;
  color: #FF6B9D;
  flex-shrink: 0;
}

.task-badge {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.badge-done {
  color: #38A169;
  background: #C6F6D5;
}

.badge-pending {
  color: #D69E2E;
  background: #FEF3C7;
}

.badge-rejected {
  color: #E53E3E;
  background: #FED7D7;
}

.badge-todo {
  color: #999;
  background: #F0F0F0;
}
</style>
