// API 封装：统一请求、token 管理
const API = {
  // Token 管理
  getToken() {
    return localStorage.getItem('token') || '';
  },
  setToken(token) {
    localStorage.setItem('token', token);
  },
  getRole() {
    return localStorage.getItem('role') || '';
  },
  setRole(role) {
    localStorage.setItem('role', role);
  },
  getUserInfo() {
    return {
      userId: localStorage.getItem('userId') || '',
      nickname: localStorage.getItem('nickname') || '',
    };
  },
  setUserInfo(userId, nickname) {
    localStorage.setItem('userId', userId);
    localStorage.setItem('nickname', nickname);
  },
  clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('userId');
    localStorage.removeItem('nickname');
  },
  isLoggedIn() {
    return !!this.getToken();
  },

  // 统一请求方法
  async request(url, options = {}) {
    const token = this.getToken();
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let body;
    if (options.body instanceof FormData) {
      body = options.body;
    } else if (options.body) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(options.body);
    }

    try {
      const res = await fetch(url, { ...options, headers, body });
      const data = await res.json();
      // 统一处理未认证（排除登录接口，登录失败也返回 -3 但不应跳转）
      if (data.code === -3 && !url.includes('/api/auth/login') && !url.includes('/api/auth/child-login')) {
        this.clearAuth();
        this.redirectToLogin();
        return data;
      }
      return data;
    } catch (e) {
      return { code: -1, msg: '网络请求失败: ' + e.message };
    }
  },

  GET(url) {
    return this.request(url, { method: 'GET' });
  },
  POST(url, body) {
    return this.request(url, { method: 'POST', body });
  },
  PUT(url, body) {
    return this.request(url, { method: 'PUT', body });
  },
  DELETE(url) {
    return this.request(url, { method: 'DELETE' });
  },
  UPLOAD(url, formData) {
    return this.request(url, { method: 'POST', body: formData });
  },

  // 登录跳转
  redirectToLogin() {
    const role = this.getRole();
    if (role === 'admin') {
      window.location.href = '/admin/login.html';
    } else if (role === 'child') {
      window.location.href = '/child/login.html';
    } else {
      window.location.href = '/';
    }
  },

  // ========== 认证 API ==========
  adminLogin(username, password) {
    return this.POST('/api/auth/login', { username, password });
  },
  childLogin(childId, pin) {
    return this.POST('/api/auth/child-login', { childId, pin });
  },
  getMe() {
    return this.GET('/api/auth/me');
  },

  // ========== 孩子端 API ==========
  getBalance() {
    return this.GET('/api/child/points/balance');
  },
  getTasks(taskType) {
    const q = taskType ? `?taskType=${taskType}` : '';
    return this.GET(`/api/child/tasks${q}`);
  },
  completeTask(taskId) {
    return this.POST(`/api/child/tasks/${taskId}/complete`);
  },
  getTaskProgress(taskType) {
    const q = taskType ? `?taskType=${taskType}` : '';
    return this.GET(`/api/child/tasks/progress${q}`);
  },
  getProducts() {
    return this.GET('/api/child/products');
  },
  redeemProduct(productId) {
    return this.POST(`/api/child/products/${productId}/redeem`);
  },
  getPointRecords(recordType, page = 1, pageSize = 20) {
    let q = `?page=${page}&pageSize=${pageSize}`;
    if (recordType) q += `&recordType=${recordType}`;
    return this.GET(`/api/child/points/records${q}`);
  },

  // ========== 家长端 API ==========
  // 任务管理
  adminGetTasks(params = {}) {
    const q = new URLSearchParams({ page: 1, pageSize: 100, ...params }).toString();
    return this.GET(`/api/admin/tasks?${q}`);
  },
  adminCreateTask(data) {
    return this.POST('/api/admin/tasks', data);
  },
  adminUpdateTask(taskId, data) {
    return this.PUT(`/api/admin/tasks/${taskId}`, data);
  },
  adminDeleteTask(taskId) {
    return this.DELETE(`/api/admin/tasks/${taskId}`);
  },
  // 商品管理
  adminGetProducts(params = {}) {
    const q = new URLSearchParams({ page: 1, pageSize: 100, ...params }).toString();
    return this.GET(`/api/admin/products?${q}`);
  },
  adminCreateProduct(data) {
    return this.POST('/api/admin/products', data);
  },
  adminUpdateProduct(productId, data) {
    return this.PUT(`/api/admin/products/${productId}`, data);
  },
  adminDeleteProduct(productId) {
    return this.DELETE(`/api/admin/products/${productId}`);
  },
  adminUploadImage(formData) {
    return this.UPLOAD('/api/admin/upload/image', formData);
  },
  // 孩子管理
  adminGetChildren() {
    return this.GET('/api/admin/children');
  },
  adminCreateChild(data) {
    return this.POST('/api/admin/children', data);
  },
  adminUpdateChild(childId, data) {
    return this.PUT(`/api/admin/children/${childId}`, data);
  },
  adminAdjustPoints(childId, data) {
    return this.POST(`/api/admin/children/${childId}/adjust-points`, data);
  },
  // 统计
  adminStatsOverview(dateRange = '7d', childId) {
    let q = `?dateRange=${dateRange}`;
    if (childId) q += `&childId=${childId}`;
    return this.GET(`/api/admin/stats/overview${q}`);
  },
  adminStatsTrend(dateRange = '7d', childId) {
    let q = `?dateRange=${dateRange}`;
    if (childId) q += `&childId=${childId}`;
    return this.GET(`/api/admin/stats/trend${q}`);
  },
};

// Toast 提示
function showToast(msg, duration = 2000) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}
