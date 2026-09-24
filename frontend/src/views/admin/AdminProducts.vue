<template>
  <div class="products-page">
    <div class="page-header">
      <h2 class="page-title">商品管理</h2>
      <button class="btn-primary" @click="openCreate">+ 新增商品</button>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-item">
        <label class="filter-label">状态</label>
        <select v-model="filters.status" class="filter-select" @change="resetAndFetch">
          <option value="">全部</option>
          <option value="on_shelf">上架中</option>
          <option value="off_shelf">已下架</option>
        </select>
      </div>
    </div>

    <!-- Product cards grid -->
    <div class="cards-grid">
      <div v-if="loading" class="card-empty">加载中...</div>
      <div v-else-if="list.length === 0" class="card-empty">暂无数据</div>
      <div v-for="product in list" :key="product.id" class="product-card">
        <div class="card-image">
          <img v-if="product.imageUrl" :src="product.imageUrl" alt="" />
          <span v-else class="image-placeholder">🎁</span>
        </div>
        <div class="card-body">
          <div class="card-title">{{ product.productName }}</div>
          <div class="card-meta">
            <span class="meta-item">
              <span class="meta-label">积分</span>
              <span class="meta-value points">{{ product.requiredPoints }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">库存</span>
              <span class="meta-value" :class="{ 'stock-zero': product.stock <= 0 }">{{ product.stock }}</span>
            </span>
          </div>
          <div class="card-badges">
            <span class="badge" :class="product.status === 'on_shelf' ? 'badge-green' : 'badge-gray'">
              {{ statusLabel(product.status) }}
            </span>
            <span class="badge" :class="product.requireReview ? 'badge-orange' : 'badge-green'">
              {{ product.requireReview ? '需审核' : '免审核' }}
            </span>
          </div>
        </div>
        <div class="card-actions">
          <button class="btn-action" @click="openEdit(product)">编辑</button>
          <button class="btn-action danger" @click="askDelete(product)">删除</button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button class="page-btn" :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span class="page-info">第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">下一页</button>
    </div>

    <!-- Create / Edit modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ editing ? '编辑商品' : '新增商品' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">商品名称 <span class="req">*</span></label>
            <input v-model="form.productName" type="text" class="form-input" placeholder="请输入商品名称" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">所需积分 <span class="req">*</span></label>
              <input v-model.number="form.requiredPoints" type="number" min="1" class="form-input" placeholder="最少 1" />
            </div>
            <div class="form-group">
              <label class="form-label">库存 <span class="req">*</span></label>
              <input v-model.number="form.stock" type="number" min="0" class="form-input" placeholder="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">状态</label>
              <select v-model="form.status" class="form-select">
                <option value="on_shelf">上架中</option>
                <option value="off_shelf">已下架</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">兑换审核</label>
              <div class="switch-wrap">
                <input v-model="form.requireReview" type="checkbox" id="requireReview" class="switch-input" />
                <label for="requireReview" class="switch-label">{{ form.requireReview ? '需要审核' : '免审核' }}</label>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">商品图片</label>
            <div class="upload-area">
              <div v-if="form.imageUrl" class="image-preview">
                <img :src="form.imageUrl" alt="预览" />
                <button class="remove-img" @click="form.imageUrl = ''" type="button">✕</button>
              </div>
              <label v-else class="upload-btn">
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  capture="environment"
                  class="file-input"
                  @change="handleUpload"
                />
                <span class="upload-icon">📷</span>
                <span>{{ uploading ? '上传中...' : '点击上传' }}</span>
                <span class="upload-hint">支持 JPG / PNG / 拍照</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input v-model.number="form.sortOrder" type="number" min="0" class="form-input" placeholder="0" />
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
        <p class="confirm-text">确定删除商品「{{ deleteTarget?.productName }}」吗？</p>
        <div class="confirm-actions">
          <button class="btn-default" @click="showDelete = false">取消</button>
          <button class="btn-danger" :disabled="submitting" @click="handleDelete">确定删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getProductList,
  createProduct,
  updateProduct,
  deleteProduct,
  uploadImage,
} from '../../api/admin'

const loading = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = 10
const total = ref(0)

const filters = reactive({ status: '' })

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const showModal = ref(false)
const editing = ref(false)
const editingId = ref(null)

const form = reactive({
  productName: '',
  requiredPoints: 1,
  stock: 0,
  status: 'on_shelf',
  imageUrl: '',
  sortOrder: 0,
  requireReview: true,
})

const showDelete = ref(false)
const deleteTarget = ref(null)

function statusLabel(s) {
  return s === 'on_shelf' ? '上架中' : '已下架'
}

function showToast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

function buildParams() {
  const params = { page: page.value, pageSize }
  if (filters.status) params.status = filters.status
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getProductList(buildParams())
    list.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function resetAndFetch() {
  page.value = 1
  fetchList()
}

function changePage(p) {
  page.value = p
  fetchList()
}

function resetForm() {
  form.productName = ''
  form.requiredPoints = 1
  form.stock = 0
  form.status = 'on_shelf'
  form.imageUrl = ''
  form.sortOrder = 0
  form.requireReview = true
}

function openCreate() {
  editing.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEdit(product) {
  editing.value = true
  editingId.value = product.id
  form.productName = product.productName
  form.requiredPoints = product.requiredPoints
  form.stock = product.stock
  form.status = product.status
  form.imageUrl = product.imageUrl || ''
  form.sortOrder = product.sortOrder ?? 0
  form.requireReview = product.requireReview ?? true
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function handleUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    showToast('仅支持 JPG / PNG 格式')
    e.target.value = ''
    return
  }
  uploading.value = true
  try {
    const res = await uploadImage(file)
    form.imageUrl = res.data.url
  } catch (e) {
    // handled by interceptor
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function handleSubmit() {
  if (!form.productName.trim()) {
    showToast('请填写商品名称')
    return
  }
  if (!form.requiredPoints || form.requiredPoints < 1) {
    showToast('所需积分至少为 1')
    return
  }
  if (form.stock < 0) {
    showToast('库存不能为负数')
    return
  }
  submitting.value = true
  try {
    const payload = {
      productName: form.productName.trim(),
      requiredPoints: Number(form.requiredPoints),
      stock: Number(form.stock),
      status: form.status,
      imageUrl: form.imageUrl || undefined,
      sortOrder: Number(form.sortOrder) || 0,
      requireReview: form.requireReview,
    }
    if (editing.value) {
      await updateProduct(editingId.value, payload)
    } else {
      await createProduct(payload)
    }
    showModal.value = false
    fetchList()
  } catch (e) {
    // handled
  } finally {
    submitting.value = false
  }
}

function askDelete(product) {
  deleteTarget.value = product
  showDelete.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await deleteProduct(deleteTarget.value.id)
    showDelete.value = false
    if (list.value.length === 1 && page.value > 1) {
      page.value--
    }
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
.products-page {
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

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.card-empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
  padding: 60px 0;
  background: #fff;
  border-radius: 12px;
}

.product-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-image {
  height: 160px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  font-size: 48px;
}

.card-body {
  padding: 16px;
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.card-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 12px;
  color: #94a3b8;
}

.meta-value {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.meta-value.points {
  color: #6366f1;
}

.meta-value.stock-zero {
  color: #ef4444;
}

.card-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-actions {
  padding: 12px 16px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 8px;
}

.btn-action {
  flex: 1;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  background: #f1f5f9;
  color: #475569;
  transition: all 0.2s;
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

.badge-green {
  background: #d1fae5;
  color: #059669;
}

.badge-gray {
  background: #e2e8f0;
  color: #64748b;
}

.badge-orange {
  background: #fed7aa;
  color: #ea580c;
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
  max-width: 500px;
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
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;
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
  width: 100%;
}

.form-input:focus,
.form-select:focus {
  border-color: #6366f1;
}

/* Switch */
.switch-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 42px;
}

.switch-input {
  width: 44px;
  height: 24px;
  appearance: none;
  background: #e2e8f0;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.switch-input::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.switch-input:checked {
  background: #6366f1;
}

.switch-input:checked::before {
  transform: translateX(20px);
}

.switch-label {
  font-size: 14px;
  color: #475569;
  cursor: pointer;
}

/* Upload */
.upload-area {
  width: 100%;
}

.image-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-img {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 120px;
  height: 120px;
  border: 1.5px dashed #cbd5e1;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}

.upload-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.upload-icon {
  font-size: 26px;
}

.upload-hint {
  font-size: 11px;
  color: #cbd5e1;
}

.file-input {
  display: none;
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
  .page-title {
    font-size: 18px;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .page-header .btn-primary {
    width: 100%;
  }

  .filter-bar {
    padding: 12px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .modal-card {
    max-width: 100%;
    margin: 10px;
    max-height: 85vh;
  }

  .modal-body {
    padding: 16px;
  }

  .form-row {
    flex-direction: column;
    gap: 12px;
  }

  .btn-action {
    padding: 10px 12px;
  }
}
</style>
