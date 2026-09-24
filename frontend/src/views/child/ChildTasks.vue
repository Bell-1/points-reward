<template>
  <div class="tasks-page">
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

    <div v-else-if="tasks.length === 0" class="empty-state">
      <span class="empty-emoji">🎈</span>
      <p>暂无任务，休息一下吧！</p>
    </div>

    <div v-else class="task-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-card"
        :class="{
          'status-pending': task.completionStatus === 'pending',
          'status-approved': task.completionStatus === 'approved',
          'status-rejected': task.completionStatus === 'rejected',
        }"
      >
        <div class="task-icon">{{ task.icon || '⭐' }}</div>
        <div class="task-info">
          <h3 class="task-name">{{ task.taskName }}</h3>
          <div class="task-reward">
            <span class="reward-star">★</span>
            <span class="reward-points">{{ task.rewardPoints }}</span>
          </div>
        </div>
        <div class="task-action">
          <span v-if="task.completionStatus === 'pending'" class="status-badge badge-pending">
            待验证
          </span>
          <span v-else-if="task.completionStatus === 'approved' && activeTab !== 'once'" class="status-badge badge-approved">
            已通过 ✓
          </span>
          <div v-else-if="task.completionStatus === 'rejected'" class="rejected-action">
            <span class="status-badge badge-rejected">已驳回</span>
            <button
              class="complete-btn"
              :disabled="completingId === task.id"
              @click="handleComplete(task.id)"
            >
              {{ completingId === task.id ? '...' : '重新提交' }}
            </button>
          </div>
          <button
            v-else
            class="complete-btn"
            :disabled="completingId === task.id"
            @click="handleComplete(task.id)"
          >
            {{ completingId === task.id ? '...' : (task.completionStatus === 'approved' ? '再次完成' : '完成') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTasks, completeTask } from '../../api/child'

const tabs = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' },
  { label: '次任务', value: 'once' },
]

const activeTab = ref('daily')
const tasks = ref([])
const loading = ref(false)
const completingId = ref(null)

async function fetchTasks() {
  loading.value = true
  try {
    const res = await getTasks(activeTab.value)
    tasks.value = res.data
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loading.value = false
  }
}

function switchTab(tabValue) {
  if (activeTab.value === tabValue) return
  activeTab.value = tabValue
  fetchTasks()
}

async function handleComplete(taskId) {
  completingId.value = taskId
  try {
    await completeTask(taskId)
    const task = tasks.value.find((t) => t.id === taskId)
    if (task) {
      task.completionStatus = 'pending'
      task.isCompleted = true
      task.completedAt = new Date().toISOString()
    }
    window.dispatchEvent(new CustomEvent('balance-update'))
    window.dispatchEvent(new CustomEvent('toast', { detail: '任务已提交，等待家长审核' }))
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    completingId.value = null
  }
}

onMounted(fetchTasks)
</script>

<style scoped>
.tasks-page {
  padding: 16px;
}

.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
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

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.15s, box-shadow 0.15s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.task-card.status-pending {
  background: linear-gradient(135deg, #FFFEF0 0%, #FEFCB8 100%);
}

.task-card.status-approved {
  background: linear-gradient(135deg, #F0FFF4 0%, #E6FFFA 100%);
}

.task-card.status-rejected {
  background: linear-gradient(135deg, #FFF0F0 0%, #FED7D7 100%);
}

.task-icon {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  border-radius: 16px;
  background: linear-gradient(135deg, #FFF0F5, #F3E8FF);
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.task-reward {
  display: flex;
  align-items: center;
  gap: 4px;
}

.reward-star {
  color: #FFD700;
  font-size: 16px;
}

.reward-points {
  font-size: 16px;
  font-weight: 700;
  color: #FF6B9D;
}

.task-action {
  flex-shrink: 0;
}

.complete-btn {
  padding: 10px 24px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.3);
  transition: transform 0.15s;
}

.complete-btn:not(:disabled):active {
  transform: scale(0.94);
}

.complete-btn:disabled {
  opacity: 0.6;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
}

.badge-pending {
  color: #D69E2E;
  background: #FEF3C7;
}

.badge-approved {
  color: #38A169;
  background: #C6F6D5;
}

.badge-rejected {
  color: #E53E3E;
  background: #FED7D7;
}

.rejected-action {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
