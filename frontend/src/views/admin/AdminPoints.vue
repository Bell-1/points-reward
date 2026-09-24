<template>
  <div class="points-page">
    <div class="page-header">
      <h2 class="page-title">积分管理</h2>
      <button class="btn-primary" @click="showAdjust = true">手动调整积分</button>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-item">
        <label class="filter-label">孩子</label>
        <select v-model="selectedChildId" class="filter-select" @change="fetchRecords">
          <option :value="null">全部孩子</option>
          <option v-for="child in children" :key="child.id" :value="child.id">
            {{ child.avatar ? child.avatar + ' ' : '' }}{{ child.nickname }}
          </option>
        </select>
      </div>
      <div class="filter-item">
        <label class="filter-label">开始日期</label>
        <input v-model="startDate" type="date" class="filter-input" @change="fetchRecords" />
      </div>
      <div class="filter-item">
        <label class="filter-label">结束日期</label>
        <input v-model="endDate" type="date" class="filter-input" @change="fetchRecords" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-box">
      <span class="loading-spinner"></span>
      <span>加载中...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="records.length === 0" class="empty-box">
      <span class="empty-icon">📊</span>
      <p>暂无积分操作记录</p>
    </div>

    <!-- Records table -->
    <div v-else class="records-container">
      <table class="records-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>孩子</th>
            <th>操作类型</th>
            <th>积分变化</th>
            <th>余额</th>
            <th>操作人</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.id">
            <td class="td-time">{{ record.createdAt }}</td>
            <td class="td-child">
              <span class="child-avatar-sm">{{ selectedChild ? selectedChild.avatar || selectedChild.nickname?.charAt(0) : '👦' }}</span>
              {{ selectedChild ? selectedChild.nickname : '-' }}
            </td>
            <td>
              <span class="badge" :class="typeBadgeClass(record.sourceType)">
                {{ typeLabel(record.sourceType) }}
              </span>
            </td>
            <td class="td-amount" :class="record.amount > 0 ? 'amount-plus' : 'amount-minus'">
              {{ record.amount > 0 ? '+' : '' }}{{ record.amount }}
            </td>
            <td class="td-balance">{{ record.balanceAfter }}</td>
            <td class="td-operator">{{ record.operatorName || '-' }}</td>
            <td class="td-remark">{{ record.remark || '-' }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination">
        <button class="page-btn" :disabled="page <= 1" @click="page--; fetchRecords()">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页，共 {{ total }} 条</span>
        <button class="page-btn" :disabled="page >= totalPages" @click="page++; fetchRecords()">下一页</button>
      </div>
    </div>
  </div>

  <!-- Adjust Modal -->
  <div v-if="showAdjust" class="modal-overlay">
    <div class="modal-box">
      <h3 class="modal-title">手动调整积分</h3>
      <div class="form-group">
        <label class="form-label">孩子</label>
        <select v-model="adjustForm.childId" class="form-select">
          <option v-for="child in children" :key="child.id" :value="child.id">
            {{ child.avatar ? child.avatar + ' ' : '' }}{{ child.nickname }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">操作类型</label>
        <div class="radio-group">
          <label class="radio-item">
            <input type="radio" v-model="adjustForm.adjustType" value="add" />
            <span class="radio-label add">增加积分</span>
          </label>
          <label class="radio-item">
            <input type="radio" v-model="adjustForm.adjustType" value="subtract" />
            <span class="radio-label subtract">扣除积分</span>
          </label>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">积分数量</label>
        <input v-model.number="adjustForm.amount" type="number" min="1" class="form-input" placeholder="请输入积分数量" />
      </div>
      <div class="form-group">
        <label class="form-label">备注</label>
        <textarea v-model="adjustForm.remark" class="form-textarea" placeholder="请输入操作备注（必填）" rows="3"></textarea>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="showAdjust = false">取消</button>
        <button class="btn-confirm" :disabled="submitting" @click="handleAdjust">
          {{ submitting ? '提交中...' : '确认' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { getChildren, getChildPointRecords, adjustPoints } from '../../api/admin'

const loading = ref(false)
const records = ref([])
const children = ref([])
const selectedChildId = ref(null)
const startDate = ref('')
const endDate = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

const showAdjust = ref(false)
const submitting = ref(false)
const adjustForm = reactive({
  childId: null,
  adjustType: 'add',
  amount: null,
  remark: '',
})

const selectedChild = computed(() => {
  if (!selectedChildId.value) return null
  return children.value.find((c) => c.id === selectedChildId.value) || null
})

function typeLabel(t) {
  return { manual_add: '手动增加', manual_deduct: '手动扣除' }[t] || t
}

function typeBadgeClass(t) {
  return { manual_add: 'badge-green', manual_deduct: 'badge-red' }[t] || 'badge-blue'
}

function toast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

async function handleAdjust() {
  if (!adjustForm.childId) return toast('请选择孩子')
  if (!adjustForm.amount || adjustForm.amount <= 0) return toast('请输入正确的积分数量')
  if (!adjustForm.remark.trim()) return toast('请输入操作备注')

  submitting.value = true
  try {
    await adjustPoints(adjustForm.childId, {
      adjustType: adjustForm.adjustType,
      amount: adjustForm.amount,
      reason: adjustForm.remark.trim(),
    })
    toast('积分调整成功')
    showAdjust.value = false
    adjustForm.amount = null
    adjustForm.remark = ''
    if (selectedChildId.value === adjustForm.childId) {
      fetchRecords()
    }
  } catch (e) {
    toast('调整失败')
  } finally {
    submitting.value = false
  }
}

async function fetchChildren() {
  try {
    const res = await getChildren()
    children.value = res.data || []
    if (children.value.length > 0 && !selectedChildId.value) {
      selectedChildId.value = children.value[0].id
    }
  } catch (e) {
    children.value = []
  }
}

async function fetchRecords() {
  if (!selectedChildId.value) return
  loading.value = true
  try {
    const params = {
      page: page.value,
      pageSize,
    }
    if (selectedChildId.value) params.childId = selectedChildId.value
    if (startDate.value) params.startDate = startDate.value
    if (endDate.value) params.endDate = endDate.value

    const res = await getChildPointRecords(selectedChildId.value, params)
    records.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    records.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchChildren()
  if (selectedChildId.value) {
    fetchRecords()
  }
})
</script>

<style scoped>
.points-page {
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

/* Filter bar */
.filter-bar {
  display: flex;
  gap: 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
}

.filter-select {
  height: 38px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  min-width: 160px;
  cursor: pointer;
}

.filter-select:focus {
  border-color: #6366f1;
}

.filter-input {
  height: 38px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
}

.filter-input:focus {
  border-color: #6366f1;
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

/* Records table */
.records-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
}

.records-table th {
  background: #f8fafc;
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.records-table td {
  padding: 14px 16px;
  font-size: 14px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.records-table tr:last-child td {
  border-bottom: none;
}

.records-table tr:hover td {
  background: #fafafa;
}

.td-time {
  color: #94a3b8;
  font-size: 13px;
  white-space: nowrap;
}

.td-child {
  display: flex;
  align-items: center;
  gap: 8px;
}

.child-avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.td-amount {
  font-weight: 700;
  font-size: 15px;
}

.amount-plus {
  color: #10b981;
}

.amount-minus {
  color: #ef4444;
}

.td-balance {
  color: #64748b;
}

.td-operator {
  color: #64748b;
}

.td-remark {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.badge-red {
  background: #fee2e2;
  color: #dc2626;
}

.badge-blue {
  background: #dbeafe;
  color: #2563eb;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
}

.page-btn {
  background: #f1f5f9;
  color: #475569;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #64748b;
}

/* Primary button */
.btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 24px;
}

.form-group {
  margin-bottom: 18px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.form-select,
.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  box-sizing: border-box;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  outline: none;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-item input[type="radio"] {
  width: 18px;
  height: 18px;
  accent-color: #6366f1;
}

.radio-label {
  font-size: 14px;
  font-weight: 600;
}

.radio-label.add {
  color: #059669;
}

.radio-label.subtract {
  color: #dc2626;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 900px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    width: 100%;
  }

  .filter-select,
  .filter-input {
    width: 100%;
  }

  .records-table {
    display: block;
    overflow-x: auto;
  }
}
</style>
