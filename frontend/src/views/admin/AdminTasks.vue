<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2 class="page-title">任务管理</h2>
      <button class="btn-primary" @click="openCreate">+ 新增任务</button>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-item">
        <label class="filter-label">状态</label>
        <select v-model="filters.isActive" class="filter-select" @change="resetAndFetch">
          <option value="">全部</option>
          <option value="true">启用</option>
          <option value="false">停用</option>
        </select>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'daily' }"
        @click="activeTab = 'daily'; resetAndFetch()"
      >
        每日任务
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'weekly' }"
        @click="activeTab = 'weekly'; resetAndFetch()"
      >
        每周任务
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'monthly' }"
        @click="activeTab = 'monthly'; resetAndFetch()"
      >
        每月任务
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'once' }"
        @click="activeTab = 'once'; resetAndFetch()"
      >
        次任务
      </button>
    </div>

    <!-- Tasks cards grid -->
    <div class="tasks-grid">
      <div v-if="loading" class="card-empty">加载中...</div>
      <div v-else-if="list.length === 0" class="card-empty">暂无数据</div>
      <div
        v-for="(task, index) in list"
        :key="task.id"
        class="task-card"
        :class="{ 'is-disabled': !task.isActive, 'drag-over': dragOverIndex === index, 'dragging': dragIndex === index }"
        draggable="true"
        @dragstart="onDragStart(index, $event)"
        @dragover.prevent="onDragOver(index)"
        @dragend="onDragEnd"
        @drop="onDrop(index)"
      >
        <div class="card-drag">
          <span class="drag-icon">☰</span>
        </div>
        <div class="card-content">
          <div class="card-header">
            <span v-if="task.icon" class="task-icon">{{ task.icon }}</span>
            <span class="task-name">{{ task.taskName }}</span>
          </div>
          <div class="card-meta">
            <span class="badge" :class="badgeClass(task.taskType)">{{ typeLabel(task.taskType) }}</span>
            <span class="points-tag">{{ task.rewardPoints }} 积分</span>
          </div>
        </div>
        <div class="card-actions">
          <button
            class="toggle-btn"
            :class="task.isActive ? 'btn-on' : 'btn-off'"
            @click="toggleActive(task)"
            type="button"
          >
            {{ task.isActive ? '停用' : '启用' }}
          </button>
          <button class="btn-action" @click="openEdit(task)">编辑</button>
          <button class="btn-action danger" @click="askDelete(task)">删除</button>
        </div>
      </div>
    </div>

    <!-- Create / Edit modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ editing ? '编辑任务' : '新增任务' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">任务名称 <span class="req">*</span></label>
            <input v-model="form.taskName" type="text" class="form-input" placeholder="请输入任务名称" />
          </div>
          <div class="form-group">
            <label class="form-label">任务类型 <span class="req">*</span></label>
            <select v-model="form.taskType" class="form-select">
              <option value="daily">每日任务</option>
              <option value="weekly">每周任务</option>
              <option value="monthly">每月任务</option>
              <option value="once">次任务</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">奖励积分 <span class="req">*</span></label>
            <input v-model.number="form.rewardPoints" type="number" min="1" max="1000" class="form-input" placeholder="1 - 1000" />
          </div>
          <div class="form-group">
            <label class="form-label">图标（可选）</label>
            <input v-model="form.icon" type="text" class="form-input" placeholder="如 📖" />
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input v-model.number="form.sortOrder" type="number" min="0" class="form-input" placeholder="数字越小越靠前" />
          </div>
          <div class="form-group toggle-row">
            <label class="form-label">启用状态</label>
            <button
              class="toggle"
              :class="{ on: form.isActive }"
              @click="form.isActive = !form.isActive"
              type="button"
            >
              <span class="toggle-knob"></span>
            </button>
            <span class="toggle-text">{{ form.isActive ? '启用' : '停用' }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-default" @click="closeModal">取消</button>
          <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="showDelete" class="modal-overlay">
      <div class="confirm-card">
        <div class="confirm-icon">🗑️</div>
        <p class="confirm-text">确定删除任务「{{ deleteTarget?.taskName }}」吗？</p>
        <div class="confirm-actions">
          <button class="btn-default" @click="showDelete = false">取消</button>
          <button class="btn-danger" :disabled="submitting" @click="handleDelete">确定删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getTaskList, createTask, updateTask, deleteTask, reorderTasks } from '../../api/admin'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])
const activeTab = ref('daily')

const dragIndex = ref(null)
const dragOverIndex = ref(null)

const filters = reactive({ isActive: '' })

const showModal = ref(false)
const editing = ref(false)
const editingId = ref(null)

const form = reactive({
  taskName: '',
  taskType: 'daily',
  rewardPoints: 10,
  icon: '',
  isActive: true,
  sortOrder: 0,
})

const showDelete = ref(false)
const deleteTarget = ref(null)

function typeLabel(t) {
  return { daily: '每日', weekly: '每周', monthly: '每月', once: '次任务' }[t] || t
}

function badgeClass(t) {
  return { daily: 'badge-blue', weekly: 'badge-green', monthly: 'badge-purple', once: 'badge-orange' }[t] || 'badge-blue'
}

function showToast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

function buildParams() {
  const params = { taskType: activeTab.value }
  if (filters.isActive !== '') params.isActive = filters.isActive
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getTaskList(buildParams())
    list.value = res.data.list || []
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function resetAndFetch() {
  fetchList()
}

function resetForm() {
  form.taskName = ''
  form.taskType = 'daily'
  form.rewardPoints = 10
  form.icon = ''
  form.isActive = true
  form.sortOrder = 0
}

function openCreate() {
  editing.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEdit(task) {
  editing.value = true
  editingId.value = task.id
  form.taskName = task.taskName
  form.taskType = task.taskType
  form.rewardPoints = task.rewardPoints
  form.icon = task.icon || ''
  form.isActive = task.isActive
  form.sortOrder = task.sortOrder ?? 0
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function handleSubmit() {
  if (!form.taskName.trim()) {
    showToast('请填写任务名称')
    return
  }
  if (!form.rewardPoints || form.rewardPoints < 1 || form.rewardPoints > 1000) {
    showToast('奖励积分需在 1 - 1000 之间')
    return
  }
  submitting.value = true
  try {
    const payload = {
      taskName: form.taskName.trim(),
      taskType: form.taskType,
      rewardPoints: Number(form.rewardPoints),
      icon: form.icon || undefined,
      isActive: form.isActive,
      sortOrder: Number(form.sortOrder) || 0,
    }
    if (editing.value) {
      await updateTask(editingId.value, payload)
    } else {
      await createTask(payload)
    }
    showModal.value = false
    fetchList()
  } catch (e) {
    // handled by interceptor
  } finally {
    submitting.value = false
  }
}

function askDelete(task) {
  deleteTarget.value = task
  showDelete.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await deleteTask(deleteTarget.value.id)
    showDelete.value = false
    fetchList()
  } catch (e) {
    // handled
  } finally {
    submitting.value = false
  }
}

async function toggleActive(task) {
  try {
    await updateTask(task.id, {
      taskName: task.taskName,
      taskType: task.taskType,
      rewardPoints: task.rewardPoints,
      icon: task.icon,
      isActive: !task.isActive,
      sortOrder: task.sortOrder,
    })
    fetchList()
  } catch (e) {
    // handled
  }
}

// ==================== 拖拽排序 ====================

function onDragStart(index, event) {
  dragIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

function onDragOver(index) {
  dragOverIndex.value = index
}

function onDrop(index) {
  if (dragIndex.value === null || dragIndex.value === index) return
  const draggedItem = list.value[dragIndex.value]
  const targetItem = list.value[index]
  const newList = [...list.value]
  newList.splice(dragIndex.value, 1)
  newList.splice(index, 0, draggedItem)
  list.value = newList
  dragIndex.value = null
  dragOverIndex.value = null
  saveOrder(newList)
}

function onDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
}

async function saveOrder(newList) {
  const taskOrders = newList.map((task, idx) => ({ id: task.id, sortOrder: idx }))
  try {
    await reorderTasks(taskOrders)
  } catch (e) {
    fetchList()
  }
}

onMounted(() => fetchList())
</script>

<style scoped>
.tasks-page {
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

/* Filters */
.filter-bar {
  display: flex;
  gap: 20px;
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
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

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.filter-select {
  height: 36px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  min-width: 140px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:focus {
  border-color: #6366f1;
}

/* Tasks Cards Grid */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.card-empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
  padding: 60px 0;
  background: #fff;
  border-radius: 12px;
}

.task-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  transition: box-shadow 0.2s, opacity 0.15s, background 0.15s;
  border-left: 4px solid #6366f1;
}

.task-card.is-disabled {
  background: #f8fafc;
  border-left-color: #cbd5e1;
}

.task-card.is-disabled .task-name {
  color: #94a3b8;
}

.task-card.is-disabled .points-tag {
  color: #94a3b8;
}

.task-card.dragging {
  opacity: 0.5;
  background: #f1f5f9;
}

.task-card.drag-over {
  background: #f0f9ff;
  box-shadow: 0 -2px 0 #6366f1;
}

.card-drag {
  cursor: grab;
  padding: 4px;
  flex-shrink: 0;
}

.card-drag:active {
  cursor: grabbing;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.task-icon {
  font-size: 18px;
}

.task-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.points-tag {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.toggle-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
  white-space: nowrap;
}

.toggle-btn.btn-on {
  background: #fef2f2;
  color: #ef4444;
}

.toggle-btn.btn-on:hover {
  background: #fee2e2;
}

.toggle-btn.btn-off {
  background: #d1fae5;
  color: #059669;
}

.toggle-btn.btn-off:hover {
  background: #a7f3d0;
}

.btn-action {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  background: #f1f5f9;
  color: #475569;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-action:hover {
  background: #e2e8f0;
}

.btn-action.danger {
  background: #fef2f2;
  color: #ef4444;
}

.btn-action.danger:hover {
  background: #fee2e2;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-blue {
  background: #dbeafe;
  color: #2563eb;
}

.badge-green {
  background: #d1fae5;
  color: #059669;
}

.badge-purple {
  background: #ede9fe;
  color: #7c3aed;
}

.badge-orange {
  background: #ffedd5;
  color: #c2410c;
}

/* Toggle switch */
.toggle {
  width: 42px;
  height: 24px;
  border-radius: 12px;
  background: #cbd5e1;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}

.toggle.on {
  background: #6366f1;
}

.toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle.on .toggle-knob {
  transform: translateX(18px);
}

/* Pagination (保留但不再使用) */
/* 注释掉 - 任务不再分页
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
*/

.page-info {
  font-size: 14px;
  color: #64748b;
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

.btn-danger {
  background: #ef4444;
  color: #fff;
  padding: 9px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link {
  background: transparent;
  color: #6366f1;
  font-size: 14px;
  padding: 4px 6px;
  transition: color 0.2s;
}

.btn-link:hover {
  color: #4f46e5;
}

.btn-link.danger {
  color: #ef4444;
}

.btn-link.danger:hover {
  color: #dc2626;
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
  max-width: 480px;
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

.toggle-row {
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.req {
  color: #ef4444;
}

.form-input,
.form-select {
  height: 42px;
  padding: 0 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
  border-color: #6366f1;
}

.toggle-text {
  font-size: 14px;
  color: #64748b;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}

/* Confirm dialog */
.confirm-card {
  background: #fff;
  border-radius: 14px;
  padding: 32px 28px 24px;
  width: 100%;
  max-width: 380px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.confirm-icon {
  font-size: 44px;
  margin-bottom: 12px;
}

.confirm-text {
  font-size: 15px;
  color: #334155;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
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

  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .tabs::-webkit-scrollbar {
    display: none;
  }

  .tasks-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .task-card {
    flex-wrap: wrap;
    padding: 12px;
  }

  .card-content {
    flex: 1 1 calc(100% - 60px);
  }

  .card-actions {
    flex-wrap: wrap;
    width: 100%;
    justify-content: flex-end;
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

  .confirm-card {
    margin: 0 8px;
  }

  .confirm-actions {
    flex-direction: column-reverse;
  }

  .confirm-actions .btn-default,
  .confirm-actions .btn-danger {
    width: 100%;
    padding: 12px 16px;
  }

  .toggle-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
