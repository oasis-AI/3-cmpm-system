import type { RouteRecordRaw } from 'vue-router'

const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue') },
      { path: 'merchants', name: 'AdminMerchants', component: () => import('@/views/admin/Merchants.vue') },
      { path: 'points-rules', name: 'AdminPointsRules', component: () => import('@/views/admin/PointsRules.vue') },
      { path: 'activities', name: 'AdminActivities', component: () => import('@/views/admin/Activities.vue') },
      { path: 'reports', name: 'AdminReports', component: () => import('@/views/admin/Reports.vue') },
      { path: 'announcements', name: 'AdminAnnouncements', component: () => import('@/views/admin/Announcements.vue') },
      { path: 'system', name: 'AdminSystem', component: () => import('@/views/admin/System.vue') },
    ],
  },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/c/Login.vue') },
]

export default adminRoutes
