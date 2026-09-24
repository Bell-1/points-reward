import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/child/login' },

  // ==================== 孩子端 ====================
  {
    path: '/child/login',
    name: 'ChildLogin',
    component: () => import('../views/child/ChildLogin.vue'),
    meta: { layout: 'blank' },
  },
  {
    path: '/child',
    component: () => import('../layouts/ChildLayout.vue'),
    meta: { requiresAuth: true, role: 'child' },
    children: [
      {
        path: 'tasks',
        name: 'ChildTasks',
        component: () => import('../views/child/ChildTasks.vue'),
      },
      {
        path: 'shop',
        name: 'ChildShop',
        component: () => import('../views/child/ChildShop.vue'),
      },
      {
        path: 'records',
        name: 'ChildRecords',
        component: () => import('../views/child/ChildRecords.vue'),
      },
      {
        path: 'redemptions',
        name: 'ChildRedemptions',
        component: () => import('../views/child/ChildRedemptions.vue'),
      },
      {
        path: 'progress',
        name: 'ChildProgress',
        component: () => import('../views/child/ChildProgress.vue'),
      },
    ],
  },

  // ==================== 家长端 ====================
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/AdminLogin.vue'),
    meta: { layout: 'blank' },
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'stats',
        name: 'AdminStats',
        component: () => import('../views/admin/AdminStats.vue'),
      },
      {
        path: 'tasks',
        name: 'AdminTasks',
        component: () => import('../views/admin/AdminTasks.vue'),
      },
      {
        path: 'reviews',
        name: 'AdminReviews',
        component: () => import('../views/admin/AdminReviews.vue'),
      },
      {
        path: 'redemptions',
        name: 'AdminRedemptions',
        component: () => import('../views/admin/AdminRedemptions.vue'),
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('../views/admin/AdminProducts.vue'),
      },
      {
        path: 'children',
        name: 'AdminChildren',
        component: () => import('../views/admin/AdminChildren.vue'),
      },
      {
        path: 'points',
        name: 'AdminPoints',
        component: () => import('../views/admin/AdminPoints.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      const loginPath = to.meta.role === 'admin' ? '/admin/login' : '/child/login'
      return next(loginPath)
    }
    if (to.meta.role && authStore.role !== to.meta.role) {
      const homePath = authStore.role === 'admin' ? '/admin/stats' : '/child/tasks'
      return next(homePath)
    }
  }
  next()
})

export default router
