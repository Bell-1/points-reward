<template>
  <div class="children-page">
    <div class="page-header">
      <h2 class="page-title">孩子管理</h2>
      <button class="btn-primary" @click="openCreate">+ 添加孩子</button>
    </div>

    <div v-if="loading" class="loading-box">
      <span class="loading-spinner"></span>
      <span>加载中...</span>
    </div>

    <div v-else-if="list.length === 0" class="empty-box">
      <span class="empty-icon">👶</span>
      <p>还没有添加孩子，点击右上角添加</p>
    </div>

    <!-- Cards grid -->
    <div v-else class="children-grid">
      <div v-for="child in list" :key="child.id" class="child-card">
        <div class="card-top">
          <div class="child-avatar">{{ avatarChar(child) }}</div>
          <div class="child-info">
            <div class="child-name">{{ child.nickname }}</div>
            <div v-if="child.age" class="child-age">{{ child.age }} 岁</div>
          </div>
        </div>
        <div class="child-balance">
          <span class="star">⭐</span>
          <span class="balance-num">{{ child.balance ?? 0 }}</span>
          <span class="balance-label">积分</span>
        </div>
        <div class="card-actions">
          <button class="btn-link" @click="openEdit(child)">编辑</button>
          <button class="btn-link primary" @click="openAdjust(child)">调整积分</button>
        </div>
      </div>
    </div>

    <!-- Add / Edit modal -->
    <div v-if="showFormModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ editing ? '编辑孩子' : '添加孩子' }}</h3>
          <button class="modal-close" @click="closeFormModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">昵称 <span class="req">*</span></label>
            <input v-model="form.nickname" type="text" class="form-input" placeholder="请输入昵称" />
          </div>
          <div class="form-group">
            <label class="form-label">年龄</label>
            <input v-model.number="form.age" type="number" min="3" max="18" class="form-input" placeholder="3 - 18（选填）" />
          </div>
          <div class="form-group">
            <label class="form-label">PIN 码 <span v-if="!editing" class="req">*</span></label>
            <input
              v-model="form.pin"
              type="text"
              maxlength="8"
              class="form-input"
              :placeholder="editing ? '留空则不修改（4-8位数字）' : '4 - 8 位数字'"
            />
          </div>
          <div class="form-group">
            <label class="form-label">头像（可选）</label>
            <input v-model="form.avatar" type="text" class="form-input" placeholder="如 🐰 或文字" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-default" @click="closeFormModal">取消</button>
          <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Adjust points modal -->
    <div v-if="showAdjustModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">调整积分</h3>
          <button class="modal-close" @click="closeAdjustModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="balance-display">
            <span class="balance-label-text">{{ adjustTarget?.nickname }} 当前积分</span>
            <span class="balance-big">{{ adjustTarget?.balance ?? 0 }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">调整方式 <span class="req">*</span></label>
            <div class="radio-group">
              <label class="radio-item">
                <input v-model="adjustForm.adjustType" type="radio" value="add" />
                <span class="radio-label">➕ 增加</span>
              </label>
              <label class="radio-item">
                <input v-model="adjustForm.adjustType" type="radio" value="subtract" />
                <span class="radio-label">➖ 减少</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">数量 <span class="req">*</span></label>
            <input v-model.number="adjustForm.amount" type="number" min="1" class="form-input" placeholder="最少 1" />
          </div>
          <div class="form-group">
            <label class="form-label">原因 <span class="req">*</span></label>
            <input v-model="adjustForm.reason" type="text" class="form-input" placeholder="请输入调整原因" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-default" @click="closeAdjustModal">取消</button>
          <button class="btn-primary" :disabled="submitting" @click="handleAdjust">
            {{ submitting ? '提交中...' : '确认调整' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getChildren, createChild, updateChild, adjustPoints } from '../../api/admin'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])

const showFormModal = ref(false)
const editing = ref(false)
const editingId = ref(null)

const form = reactive({
  nickname: '',
  age: null,
  pin: '',
  avatar: '',
})

const showAdjustModal = ref(false)
const adjustTarget = ref(null)

const adjustForm = reactive({
  adjustType: 'add',
  amount: 1,
  reason: '',
})

function avatarChar(child) {
  if (child.avatar) return child.avatar
  return (child.nickname || '?').charAt(0)
}

function showToast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getChildren()
    list.value = res.data || []
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.nickname = ''
  form.age = null
  form.pin = ''
  form.avatar = ''
}

function openCreate() {
  editing.value = false
  editingId.value = null
  resetForm()
  showFormModal.value = true
}

function openEdit(child) {
  editing.value = true
  editingId.value = child.id
  form.nickname = child.nickname
  form.age = child.age ?? null
  form.pin = ''
  form.avatar = child.avatar || ''
  showFormModal.value = true
}

function closeFormModal() {
  showFormModal.value = false
}

async function handleSubmit() {
  if (!form.nickname.trim()) {
    showToast('请填写昵称')
    return
  }
  if (!editing.value) {
    if (!form.pin) {
      showToast('请填写 PIN 码')
      return
    }
    if (!/^\d{4,8}$/.test(form.pin)) {
      showToast('PIN 码需为 4 - 8 位数字')
      return
    }
  } else if (form.pin && !/^\d{4,8}$/.test(form.pin)) {
    showToast('PIN 码需为 4 - 8 位数字')
    return
  }
  if (form.age !== null && form.age !== '' && (form.age < 3 || form.age > 18)) {
    showToast('年龄需在 3 - 18 之间')
    return
  }
  submitting.value = true
  try {
    if (editing.value) {
      const payload = {
        nickname: form.nickname.trim(),
        age: form.age || undefined,
        avatar: form.avatar || undefined,
      }
      if (form.pin) payload.pin = form.pin
      await updateChild(editingId.value, payload)
    } else {
      const payload = {
        nickname: form.nickname.trim(),
        age: form.age || undefined,
        avatar: form.avatar || undefined,
        pin: form.pin,
      }
      await createChild(payload)
    }
    showFormModal.value = false
    fetchList()
  } catch (e) {
    // handled by interceptor
  } finally {
    submitting.value = false
  }
}

function openAdjust(child) {
  adjustTarget.value = child
  adjustForm.adjustType = 'add'
  adjustForm.amount = 1
  adjustForm.reason = ''
  showAdjustModal.value = true
}

function closeAdjustModal() {
  showAdjustModal.value = false
}

async function handleAdjust() {
  if (!adjustTarget.value) return
  if (!adjustForm.amount || adjustForm.amount < 1) {
    showToast('数量至少为 1')
    return
  }
  if (!adjustForm.reason.trim()) {
    showToast('请填写调整原因')
    return
  }
  submitting.value = true
  try {
    await adjustPoints(adjustTarget.value.id, {
      adjustType: adjustForm.adjustType,
      amount: Number(adjustForm.amount),
      reason: adjustForm.reason.trim(),
    })
    showAdjustModal.value = false
    fetchList()
  } catch (e) {
    // handled
  } finally {
    submitting.value = false
  }
}

onMounted(() => fetchList())
</script>

<style scoped>
.children-page {
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

/* Cards grid */
.children-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.child-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: box-shadow 0.2s, transform 0.2s;
}

.child-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 14px;
}

.child-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  flex-shrink: 0;
}

.child-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.child-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.child-age {
  font-size: 13px;
  color: #94a3b8;
}

.child-balance {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 12px 16px;
  background: #fef9c3;
  border-radius: 10px;
}

.star {
  font-size: 18px;
}

.balance-num {
  font-size: 24px;
  font-weight: 700;
  color: #92400e;
  line-height: 1;
}

.balance-label {
  font-size: 13px;
  color: #b45309;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* Buttons */
.btn-primary {
  background: #6366f1;
  color: #fff;
  padding: 9px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #4f46e5;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-default {
  background: #f1f5f9;
  color: #475569;
  padding: 9px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-default:hover {
  background: #e2e8f0;
}

.btn-link {
  flex: 1;
  background: #f1f5f9;
  color: #475569;
  padding: 8px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  text-align: center;
}

.btn-link:hover {
  background: #e2e8f0;
}

.btn-link.primary {
  background: #eef2ff;
  color: #6366f1;
}

.btn-link.primary:hover {
  background: #e0e7ff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-card {
  background: #fff;
  border-radius: 14px;
  width: 100%;
  max-width: 460px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
}

.modal-close {
  font-size: 18px;
  color: #94a3b8;
  background: transparent;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #475569;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
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

.req {
  color: #ef4444;
}

.form-input {
  height: 42px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #6366f1;
}

/* Balance display in adjust modal */
.balance-display {
  text-align: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.balance-label-text {
  font-size: 13px;
  color: #94a3b8;
}

.balance-big {
  font-size: 32px;
  font-weight: 700;
  color: #6366f1;
  line-height: 1;
}

/* Radio group */
.radio-group {
  display: flex;
  gap: 16px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.radio-item:has(input:checked) {
  border-color: #6366f1;
  background: #eef2ff;
}

.radio-item input {
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
}

.radio-label {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .btn-primary {
    width: 100%;
    text-align: center;
    padding: 12px 16px;
  }

  .children-grid {
    grid-template-columns: 1fr;
  }

  .modal-card {
    max-width: 100%;
    margin: 0 8px;
  }

  .modal-body {
    padding: 16px;
  }

  .form-group {
    gap: 6px;
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 10px;
  }

  .modal-footer .btn-default,
  .modal-footer .btn-primary {
    width: 100%;
    text-align: center;
    padding: 12px 16px;
  }

  .radio-group {
    flex-direction: column;
    gap: 10px;
  }

  .radio-item {
    width: 100%;
    justify-content: center;
  }

  .card-actions {
    flex-direction: column;
    gap: 8px;
  }

  .btn-link {
    width: 100%;
  }
}
</style>
