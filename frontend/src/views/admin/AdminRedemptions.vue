<template>
  <div class="redemptions-page">
    <div class="page-header">
      <h2 class="page-title">兑换审核</h2>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'pending' }"
        @click="activeTab = 'pending'"
      >
        待审核
        <span v-if="pendingCount" class="tab-count">{{ pendingCount }}</span>
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'approved' }"
        @click="activeTab = 'approved'"
      >
        已通过
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-box">
      <span class="loading-spinner"></span>
      <span>加载中...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredList.length === 0" class="empty-box">
      <span class="empty-icon">🎁</span>
      <p>{{ emptyText }}</p>
    </div>

    <!-- Redemption cards -->
    <div v-else class="redemption-list">
      <div v-for="item in filteredList" :key="item.id" class="redemption-card">
        <div class="card-top-row">
          <div class="child-block">
            <span class="child-avatar">{{ getChildAvatar(item.childId) }}</span>
            <span class="child-name">{{ item.childName }}</span>
          </div>
          <span class="badge" :class="statusBadgeClass(item.status)">{{ statusLabel(item.status) }}</span>
        </div>

        <div class="card-body">
          <div class="product-info">
            <span class="product-name">{{ item.productName }}</span>
          </div>
          <div class="meta-row">
            <span class="cost-points">🎁 {{ item.pointsCost }} 积分</span>
            <span class="redeemed-time">📅 {{ formatTime(item.redeemedAt) }}</span>
          </div>
        </div>

        <!-- Action area (pending only) -->
        <div v-if="item.status === 'pending'" class="action-area">
          <div class="action-buttons">
            <button
              class="btn-approve"
              :disabled="processingId === item.id"
              @click="handleReview(item, true)"
            >
              {{ processingId === item.id ? '处理中...' : '通过' }}
            </button>
            <button
              class="btn-reject"
              :disabled="processingId === item.id"
              @click="handleReview(item, false)"
            >
              {{ processingId === item.id ? '处理中...' : '驳回' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination (approved only) -->
    <div v-if="activeTab === 'approved' && total > 0" class="pagination">
      <button class="page-btn" :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span class="page-info">第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPendingRedemptions, getApprovedRedemptions, reviewRedemption } from '../../api/admin'

const loading = ref(false)
const processingId = ref(null)
const pendingList = ref([])
const approvedList = ref([])
const activeTab = ref('pending')
const page = ref(1)
const pageSize = 20
const total = ref(0)

const pendingCount = computed(() => pendingList.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const filteredList = computed(() => {
  if (activeTab.value === 'pending') {
    return pendingList.value
  }
  return approvedList.value
})

const emptyText = computed(() => {
  return activeTab.value === 'pending' ? '暂无待审核兑换' : '暂无已通过记录'
})

function statusLabel(s) {
  return { pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s
}

function statusBadgeClass(s) {
  return { pending: 'badge-yellow', approved: 'badge-green', rejected: 'badge-red' }[s] || 'badge-yellow'
}

function getChildAvatar(childId) {
  // Just use first character of name or default
  return '👦'
}

function formatTime(time) {
  if (!time) return ''
  const d = new Date(time)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function showToast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

async function fetchPending() {
  try {
    const res = await getPendingRedemptions()
    pendingList.value = res.data || []
  } catch (e) {
    pendingList.value = []
  }
}

async function fetchApproved() {
  loading.value = true
  try {
    const res = await getApprovedRedemptions({ page: page.value, pageSize })
    approvedList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    approvedList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function handleReview(item, approved) {
  processingId.value = item.id
  try {
    await reviewRedemption(item.id, approved)
    showToast(approved ? '兑换已通过' : '兑换已驳回，积分已返还')
    // Remove from pending list
    pendingList.value = pendingList.value.filter((r) => r.id !== item.id)
    window.dispatchEvent(new CustomEvent('balance-update'))
    window.dispatchEvent(new CustomEvent('redemptions-updated'))
  } catch (e) {
    // handled by interceptor
  } finally {
    processingId.value = null
  }
}

function changePage(p) {
  page.value = p
  fetchApproved()
}

onMounted(async () => {
  await Promise.all([fetchPending(), fetchApproved()])
})
</script>

<style scoped>
.redemptions-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
}

.tab {
  background: transparent;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab:hover {
  background: #fff;
  color: #334155;
}

.tab.active {
  background: #fff;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: #6366f1;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.tab:not(.active) .tab-count {
  background: #cbd5e1;
}

/* Loading */
.loading-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 80px 0;
  color: #94a3b8;
  font-size: 15px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty */
.empty-box {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

/* Redemption list */
.redemption-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.redemption-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: box-shadow 0.2s;
}

.redemption-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.child-block {
  display: flex;
  align-items: center;
  gap: 10px;
}

.child-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.child-name {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.cost-points {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
}

.redeemed-time {
  font-size: 13px;
  color: #94a3b8;
}

/* Action area */
.action-area {
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-approve {
  background: #10b981;
  color: #fff;
  padding: 9px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-approve:hover:not(:disabled) {
  background: #059669;
}

.btn-reject {
  background: #ef4444;
  color: #fff;
  padding: 9px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-reject:hover:not(:disabled) {
  background: #dc2626;
}

.btn-approve:disabled,
.btn-reject:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-green {
  background: #d1fae5;
  color: #059669;
}

.badge-yellow {
  background: #fef9c3;
  color: #b45309;
}

.badge-red {
  background: #fee2e2;
  color: #dc2626;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.page-btn {
  padding: 8px 18px;
  border-radius: 6px;
  background: #fff;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  color: #475569;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #6366f1;
  color: #6366f1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #64748b;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .tabs::-webkit-scrollbar {
    display: none;
  }

  .redemption-card {
    margin: 0 4px;
  }

  .card-top-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .action-area {
    gap: 10px;
  }

  .action-buttons {
    flex-direction: column-reverse;
    gap: 8px;
  }

  .btn-approve,
  .btn-reject {
    width: 100%;
    text-align: center;
    padding: 12px 16px;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .page-btn {
    width: 100%;
    padding: 12px 16px;
  }
}
</style>
