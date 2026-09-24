import request from './request'

// ==================== 任务管理 ====================

export function getTaskList(params) {
  return request.get('/api/admin/tasks', { params })
}

export function createTask(data) {
  return request.post('/api/admin/tasks', data)
}

export function updateTask(taskId, data) {
  return request.put(`/api/admin/tasks/${taskId}`, data)
}

export function deleteTask(taskId) {
  return request.delete(`/api/admin/tasks/${taskId}`)
}

export function reorderTasks(taskOrders) {
  return request.put('/api/admin/tasks/reorder', { taskOrders })
}

// ==================== 任务审核 ====================

export function getPendingReviews(childId) {
  return request.get('/api/admin/tasks/pending', { params: { childId } })
}

export function getReviewedReviews(params) {
  return request.get('/api/admin/tasks/reviewed', { params })
}

export function reviewCompletion(completionId, action, comment) {
  return request.post(`/api/admin/tasks/${completionId}/review`, { action, comment })
}

// ==================== 兑换审核 ====================

export function getPendingRedemptions() {
  return request.get('/api/admin/redemptions/pending')
}

export function getApprovedRedemptions(params) {
  return request.get('/api/admin/redemptions/approved', { params })
}

export function reviewRedemption(redemptionId, approved) {
  return request.post(`/api/admin/redemptions/${redemptionId}/review`, { approved })
}

// ==================== 商品管理 ====================

export function getProductList(params) {
  return request.get('/api/admin/products', { params })
}

export function createProduct(data) {
  return request.post('/api/admin/products', data)
}

export function updateProduct(productId, data) {
  return request.put(`/api/admin/products/${productId}`, data)
}

export function deleteProduct(productId) {
  return request.delete(`/api/admin/products/${productId}`)
}

// ==================== 图片上传 ====================

export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/admin/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ==================== 孩子管理 ====================

export function getChildren() {
  return request.get('/api/admin/children')
}

export function createChild(data) {
  return request.post('/api/admin/children', data)
}

export function updateChild(childId, data) {
  return request.put(`/api/admin/children/${childId}`, data)
}

export function adjustPoints(childId, data) {
  return request.post(`/api/admin/children/${childId}/adjust-points`, data)
}

export function getChildPointRecords(childId, params) {
  return request.get(`/api/admin/children/${childId}/points/records`, { params })
}

// ==================== 数据统计 ====================

export function getStatsOverview(params) {
  return request.get('/api/admin/stats/overview', { params })
}

export function getStatsTrend(params) {
  return request.get('/api/admin/stats/trend', { params })
}
