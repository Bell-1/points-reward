<template>
  <div class="redemptions-page">
    <div class="page-header">
      <h2 class="page-title">兑换记录</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="loading-emoji">⏳</span>
      <p>加载中...</p>
    </div>

    <div v-else-if="records.length === 0" class="empty-state">
      <span class="empty-emoji">🎁</span>
      <p>暂无兑换记录</p>
    </div>

    <template v-else>
      <div class="records-list">
        <div v-for="record in records" :key="record.id" class="record-item">
          <div class="record-header">
            <div class="product-info">
              <span class="product-icon">🎁</span>
              <span class="product-name">{{ record.productName }}</span>
            </div>
            <span class="badge" :class="statusBadgeClass(record.status)">
              {{ statusLabel(record.status) }}
            </span>
          </div>

          <div class="record-body">
            <div class="info-row">
              <span class="info-label">消耗积分</span>
              <span class="info-value cost">-{{ record.pointsCost }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">申请时间</span>
              <span class="info-value">{{ record.redeemedAt }}</span>
            </div>
            <div v-if="record.reviewedAt" class="info-row">
              <span class="info-label">审核时间</span>
              <span class="info-value">{{ record.reviewedAt }}</span>
            </div>
          </div>

          <!-- Pending message -->
          <div v-if="record.status === 'pending'" class="status-tip pending-tip">
            ⏳ 等待家长审核中，审核通过后将正式扣减积分
          </div>

          <!-- Approved message -->
          <div v-if="record.status === 'approved'" class="status-tip approved-tip">
            ✅ 兑换成功，商品已发放
          </div>

          <!-- Rejected message -->
          <div v-if="record.status === 'rejected'" class="status-tip rejected-tip">
            ❌ 兑换已驳回，积分已返还到账户
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
import { getRedemptions } from '../../api/child'

const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function statusLabel(s) {
  return { pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s
}

function statusBadgeClass(s) {
  return { pending: 'badge-yellow', approved: 'badge-green', rejected: 'badge-red' }[s] || 'badge-yellow'
}

async function fetchRecords() {
  loading.value = true
  try {
    const res = await getRedemptions(page.value, pageSize)
    records.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loading.value = false
  }
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchRecords()
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.redemptions-page {
  padding: 16px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
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
  gap: 14px;
}

.record-item {
  padding: 16px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-icon {
  font-size: 20px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.record-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.info-label {
  color: #94a3b8;
  min-width: 70px;
}

.info-value {
  color: #475569;
  font-weight: 500;
}

.info-value.cost {
  color: #ef4444;
  font-weight: 700;
}

.status-tip {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
}

.pending-tip {
  background: #fef9c3;
  color: #92400e;
}

.approved-tip {
  background: #d1fae5;
  color: #065f46;
}

.rejected-tip {
  background: #fee2e2;
  color: #991b1b;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-yellow {
  background: #fef9c3;
  color: #92400e;
}

.badge-green {
  background: #d1fae5;
  color: #065f46;
}

.badge-red {
  background: #fee2e2;
  color: #991b1b;
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
