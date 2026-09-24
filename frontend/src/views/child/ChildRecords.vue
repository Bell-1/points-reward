<template>
  <div class="records-page">
    <div class="balance-card">
      <span class="balance-label">我的积分</span>
      <span class="balance-value">
        <span class="balance-star">★</span>{{ balance }}
      </span>
    </div>

    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.value ?? 'all'"
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

    <div v-else-if="records.length === 0" class="empty-state">
      <span class="empty-emoji">📭</span>
      <p>暂无记录</p>
    </div>

    <template v-else>
      <div class="records-list">
        <div v-for="record in records" :key="record.id" class="record-item">
          <div class="record-icon" :class="record.amount >= 0 ? 'earning' : 'spending'">
            {{ record.amount >= 0 ? '📈' : '📉' }}
          </div>
          <div class="record-info">
            <div class="record-top">
              <span class="record-source">{{ record.sourceName }}</span>
              <span class="record-amount" :class="record.amount >= 0 ? 'positive' : 'negative'">
                {{ record.amount >= 0 ? '+' : '' }}{{ record.amount }}
              </span>
            </div>
            <div class="record-bottom">
              <span class="record-remark">{{ record.remark || record.sourceType }}</span>
              <span class="record-time">{{ formatTime(record.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="page <= 1" @click="changePage(page - 1)">
          ← 上一页
        </button>
        <span class="page-num">{{ page }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">
          下一页 →
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPointRecords, getBalance } from '../../api/child'

const tabs = [
  { label: '全部', value: null },
  { label: '获取', value: 'earning' },
  { label: '兑换', value: 'spending' },
]

const activeTab = ref(null)
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const balance = ref(0)
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function fetchRecords() {
  loading.value = true
  try {
    const res = await getPointRecords(activeTab.value, page.value, pageSize)
    records.value = res.data.list
    total.value = res.data.total
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loading.value = false
  }
}

async function fetchBalance() {
  try {
    const res = await getBalance()
    balance.value = res.data.balance
  } catch (e) {
    /* interceptor shows toast */
  }
}

function switchTab(tabValue) {
  if (activeTab.value === tabValue) return
  activeTab.value = tabValue
  page.value = 1
  fetchRecords()
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchRecords()
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${mm}-${dd} ${hh}:${mi}`
}

onMounted(() => {
  fetchRecords()
  fetchBalance()
})
</script>

<style scoped>
.records-page {
  padding: 16px;
}

.balance-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  margin-bottom: 20px;
  border-radius: 24px;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 16px rgba(199, 125, 255, 0.3);
}

.balance-label {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.balance-value {
  font-size: 32px;
  font-weight: 800;
  color: #fff;
}

.balance-star {
  color: #FFD700;
  margin-right: 4px;
}

.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #999;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.tab-btn.active {
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 12px rgba(199, 125, 255, 0.3);
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

.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.record-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  border-radius: 14px;
}

.record-icon.earning {
  background: #E6FFFA;
}

.record-icon.spending {
  background: #FFF0F0;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.record-source {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-amount {
  font-size: 18px;
  font-weight: 800;
  flex-shrink: 0;
  margin-left: 8px;
}

.record-amount.positive {
  color: #38A169;
}

.record-amount.negative {
  color: #E53E3E;
}

.record-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.record-remark {
  font-size: 13px;
  color: #aaa;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-time {
  font-size: 13px;
  color: #bbb;
  flex-shrink: 0;
  margin-left: 8px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 10px 20px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.25);
  transition: opacity 0.2s, transform 0.15s;
}

.page-btn:not(:disabled):active {
  transform: scale(0.95);
}

.page-btn:disabled {
  opacity: 0.4;
}

.page-num {
  font-size: 16px;
  font-weight: 700;
  color: #888;
}
</style>
