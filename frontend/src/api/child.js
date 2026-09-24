import request from './request'

// 获取积分余额
export function getBalance() {
  return request.get('/api/child/points/balance')
}

// 获取任务列表
export function getTasks(taskType) {
  return request.get('/api/child/tasks', { params: { taskType } })
}

// 完成任务
export function completeTask(taskId) {
  return request.post(`/api/child/tasks/${taskId}/complete`)
}

// 获取任务进度
export function getTaskProgress(taskType) {
  return request.get('/api/child/tasks/progress', { params: { taskType } })
}

// 获取商品列表
export function getProducts() {
  return request.get('/api/child/products')
}

// 兑换商品
export function redeemProduct(productId) {
  return request.post(`/api/child/products/${productId}/redeem`)
}

// 获取积分记录
export function getPointRecords(recordType, page = 1, pageSize = 20) {
  return request.get('/api/child/points/records', { params: { recordType, page, pageSize } })
}

// 获取兑换记录
export function getRedemptions(page = 1, pageSize = 20) {
  return request.get('/api/child/redemptions', { params: { page, pageSize } })
}
