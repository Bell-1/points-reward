// 孩子端公共逻辑

// 检查登录状态
async function checkChildAuth() {
  if (!API.isLoggedIn() || API.getRole() !== 'child') {
    window.location.href = '/child/login.html';
    return false;
  }
  // 验证 token 有效性
  const res = await API.getMe();
  if (res.code !== 0) {
    API.clearAuth();
    window.location.href = '/child/login.html';
    return false;
  }
  return true;
}

// 获取当前孩子信息
async function getChildInfo() {
  const res = await API.getMe();
  return res.code === 0 ? res.data : null;
}

// 底部导航栏
function renderTabbar(active) {
  const items = [
    { key: 'tasks', label: '任务', icon: '✅', href: '/child/tasks.html' },
    { key: 'shop', label: '商店', icon: '🎁', href: '/child/shop.html' },
    { key: 'records', label: '记录', icon: '📋', href: '/child/records.html' },
    { key: 'progress', label: '进度', icon: '📊', href: '/child/progress.html' },
  ];
  return items.map(i =>
    `<a class="tabbar__item ${i.key === active ? 'active' : ''}" href="${i.href}">
      <span class="tabbar__icon">${i.icon}</span>${i.label}
    </a>`
  ).join('');
}

// 确认弹窗
function showConfirm(title, message, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay show';
  overlay.innerHTML = `
    <div class="modal">
      <h3>${title}</h3>
      <p>${message}</p>
      <div class="modal__actions">
        <button class="btn btn--secondary">取消</button>
        <button class="btn btn--primary confirm-btn">确定</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.querySelector('.btn--secondary').onclick = () => overlay.remove();
  overlay.querySelector('.confirm-btn').onclick = () => {
    overlay.remove();
    onConfirm();
  };
}

// 任务类型名称
const taskTypeLabels = { daily: '日常任务', weekly: '周任务', monthly: '月度任务' };
const taskTypeIcons = { daily: '📅', weekly: '📆', monthly: '🗓️' };
