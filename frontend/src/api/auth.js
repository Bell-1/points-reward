import request from './request'

// 家长登录
export function adminLogin(username, password) {
  return request.post('/api/auth/login', { username, password })
}

// 孩子登录
export function childLogin(childId, pin) {
  return request.post('/api/auth/child-login', { childId, pin })
}

// 获取当前用户信息
export function getMe() {
  return request.get('/api/auth/me')
}

// 获取孩子列表（公开接口）
export function getChildrenList() {
  return request.get('/api/auth/children-list')
}
