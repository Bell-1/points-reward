// 家长端公共逻辑

// 检查登录状态
async function checkAdminAuth() {
  if (!API.isLoggedIn() || API.getRole() !== 'admin') {
    window.location.href = '/admin/login.html';
    return false;
  }
  const res = await API.getMe();
  if (res.code !== 0 || res.data.role !== 'admin') {
    API.clearAuth();
    window.location.href = '/admin/login.html';
    return false;
  }
  return true;
}

// 侧边栏
function renderSidebar(active) {
  const items = [
    { key: 'stats', label: '数据统计', icon: '📊', href: '/admin/stats.html' },
    { key: 'tasks', label: '任务管理', icon: '✅', href: '/admin/tasks.html' },
    { key: 'products', label: '商品管理', icon: '🎁', href: '/admin/products.html' },
    { key: 'children', label: '孩子管理', icon: '👶', href: '/admin/children.html' },
  ];
  const userInfo = API.getUserInfo();
  return `
    <div class="sidebar">
      <div class="sidebar__logo">积分奖励平台</div>
      <nav class="sidebar__nav">
        ${items.map(i => `
          <a class="sidebar__item ${i.key === active ? 'active' : ''}" href="${i.href}">
            <span class="sidebar__icon">${i.icon}</span>${i.label}
          </a>
        `).join('')}
      </nav>
      <div class="sidebar__footer">
        <div class="sidebar__user">${userInfo.nickname || '管理员'}</div>
        <button class="sidebar__logout" onclick="logoutAdmin()">退出登录</button>
      </div>
    </div>`;
}

function logoutAdmin() {
  API.clearAuth();
  window.location.href = '/admin/login.html';
}

// 模态框
function showModal(title, bodyHTML) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay show';
  overlay.id = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal-box" id="modal-box">
      <h3>${title}</h3>
      ${bodyHTML}
      <div class="modal-box__actions">
        <button class="btn" onclick="closeModal()">取消</button>
        <button class="btn btn--primary" id="modal-save-btn">保存</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) closeModal(); };
  return overlay;
}

function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.remove();
}

// 确认弹窗
function showConfirm(title, message, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay show';
  overlay.innerHTML = `
    <div class="modal-box">
      <h3>${title}</h3>
      <p style="color:var(--text-muted); margin-bottom: 20px;">${message}</p>
      <div class="modal-box__actions">
        <button class="btn">取消</button>
        <button class="btn btn--danger confirm-btn">确定</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.querySelector('.btn').onclick = () => overlay.remove();
  overlay.querySelector('.confirm-btn').onclick = () => { overlay.remove(); onConfirm(); };
}

// 任务/商品类型名称
const adminTaskTypes = { daily: '日常', weekly: '周任务', monthly: '月度' };
const adminProductStatus = { on_shelf: '上架', off_shelf: '下架' };

// 可选图标
const taskIcons = ['📝', '📚', '🛏️', '🏃', '🧹', '🦷', '💧', '🥗', '📖', '🎨', '🎵', '⚽'];
const childAvatars = ['👦', '👧', '🧒', '👶', '🐱', '🐰', '🦊', '🐼'];
