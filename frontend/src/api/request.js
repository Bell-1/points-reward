import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const request = axios.create({
  baseURL: '',
  timeout: 15000,
})

// 请求拦截器：自动添加 token
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Toast 函数（挂载到 window 上由 Toast 组件驱动）
function showToast(msg) {
  window.dispatchEvent(new CustomEvent('toast', { detail: msg }))
}

// 响应拦截器：统一处理 {code, data, msg}
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 0) {
      return res
    }
    // 业务错误
    showToast(res.msg || '操作失败')
    return Promise.reject(new Error(res.msg || '操作失败'))
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401 || (data && data.code === -3)) {
        const authStore = useAuthStore()
        authStore.logout()
        const role = authStore.role
        if (role === 'child') {
          router.push('/child/login')
        } else {
          router.push('/admin/login')
        }
        showToast('登录已过期，请重新登录')
      } else {
        showToast((data && data.msg) || `请求错误 (${status})`)
      }
    } else {
      showToast('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
