import type { RouteRecordRaw } from 'vue-router'

const merchantRoutes: RouteRecordRaw[] = [
  {
    path: '/merchant',
    component: () => import('@/layouts/MerchantLayout.vue'),
    meta: { requiresMerchant: true },
    children: [
      { path: '', redirect: '/merchant/dashboard' },
      { path: 'dashboard', name: 'MerchantDashboard', component: () => import('@/views/merchant/Dashboard.vue') },
      { path: 'products', name: 'MerchantProducts', component: () => import('@/views/merchant/Products.vue') },
      { path: 'inventory', name: 'MerchantInventory', component: () => import('@/views/merchant/Inventory.vue') },
      { path: 'orders', name: 'MerchantOrders', component: () => import('@/views/merchant/Orders.vue') },
      { path: 'analytics', name: 'MerchantAnalytics', component: () => import('@/views/merchant/Analytics.vue') },
      { path: 'activities', name: 'MerchantActivities', component: () => import('@/views/merchant/Activities.vue') },
    ],
  },
  { path: '/merchant/login', name: 'MerchantLogin', component: () => import('@/views/c/Login.vue') },
]

export default merchantRoutes
