import type { RouteRecordRaw } from 'vue-router'

const cRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/CLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/c/Home.vue') },
      { path: 'products', name: 'ProductList', component: () => import('@/views/c/ProductList.vue') },
      { path: 'products/:id', name: 'ProductDetail', component: () => import('@/views/c/ProductDetail.vue') },
      { path: 'search', name: 'Search', component: () => import('@/views/c/Search.vue') },
      { path: 'cart', name: 'Cart', component: () => import('@/views/c/Cart.vue'), meta: { requiresAuth: true } },
      { path: 'checkout', name: 'Checkout', component: () => import('@/views/c/Checkout.vue'), meta: { requiresAuth: true } },
      { path: 'recharge', name: 'Recharge', component: () => import('@/views/c/Recharge.vue'), meta: { requiresAuth: true } },
      { path: 'activities', name: 'Activities', component: () => import('@/views/c/Activities.vue') },
      { path: 'announcements', name: 'Announcements', component: () => import('@/views/c/Announcements.vue') },
      { path: 'announcements/:id', name: 'AnnouncementDetail', component: () => import('@/views/c/AnnouncementDetail.vue') },
      {
        path: 'user',
        meta: { requiresAuth: true },
        children: [
          { path: '', name: 'UserDashboard', component: () => import('@/views/c/user/Dashboard.vue') },
          { path: 'profile', name: 'UserProfile', component: () => import('@/views/c/user/Profile.vue') },
          { path: 'points', name: 'UserPoints', component: () => import('@/views/c/user/Points.vue') },
          { path: 'orders', name: 'UserOrders', component: () => import('@/views/c/user/Orders.vue') },
          { path: 'addresses', name: 'UserAddresses', component: () => import('@/views/c/user/Addresses.vue') },
          { path: 'addresses/new', name: 'UserAddressNew', component: () => import('@/views/c/user/Address.vue') },
          { path: 'addresses/:id/edit', name: 'UserAddressEdit', component: () => import('@/views/c/user/Address.vue') },
        ],
      },
    ],
  },
  { path: '/login', name: 'Login', component: () => import('@/views/c/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/c/Register.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/c/NotFound.vue') },
]

export default cRoutes
