import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import cRoutes from './c.routes'
import merchantRoutes from './merchant.routes'
import adminRoutes from './admin.routes'

const routes: RouteRecordRaw[] = [...cRoutes, ...merchantRoutes, ...adminRoutes]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// ---------- 全局路由守卫 ----------
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // 需要登录的路由
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 需要商户权限
  if (to.meta.requiresMerchant) {
    if (!authStore.isLoggedIn) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    if (!authStore.isMerchant) {
      next({ path: '/' })
      return
    }
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin) {
    if (!authStore.isLoggedIn) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    if (!authStore.isAdmin) {
      next({ path: '/' })
      return
    }
  }

  next()
})

export default router
