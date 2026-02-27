<template>
  <div class="c-layout">
    <header class="c-header">
      <div class="header-inner">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <div class="logo-icon">移</div>
          <div class="logo-texts">
            <span class="logo-main">积分商城</span>
            <span class="logo-sub">China Mobile</span>
          </div>
        </router-link>

        <!-- 搜索框 -->
        <div class="search-wrap">
          <div class="search-bar">
            <input
              v-model="keyword"
              class="search-input"
              placeholder="搜索商品、礼品、话费充值..."
              @keyup.enter="doSearch"
            />
            <button class="search-btn" @click="doSearch">
              <el-icon><Search /></el-icon> 搜索
            </button>
          </div>
          <div class="hot-search">
            <span class="hot-label">热门搜索：</span>
            <a v-for="kw in hotKeywords" :key="kw" class="hot-tag"
               @click="quickSearch(kw)">{{ kw }}</a>
          </div>
        </div>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 购物车 -->
          <router-link to="/cart" class="cart-box">
            <el-badge :value="cartStore.count || ''" :hidden="!cartStore.count">
              <el-icon :size="28"><ShoppingCart /></el-icon>
            </el-badge>
            <span>购物车</span>
          </router-link>

          <!-- 用户头像 -->
          <template v-if="authStore.isLoggedIn">
            <el-dropdown @command="handleUserCmd">
              <span class="user-trigger">
                <el-avatar :size="36" :src="authStore.userInfo?.avatar" />
                <div class="user-info-mini">
                  <span class="nickname">{{ authStore.userInfo?.nickname }}</span>
                  <span class="usr-pts">积分：{{ authStore.userInfo?.points_balance ?? '—' }}</span>
                </div>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                  <el-dropdown-item command="points">积分明细</el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isMerchant" command="merchant" divided>商家后台</el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" command="admin" divided>管理后台</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>

      <!-- 导航条 -->
      <nav class="header-nav">
        <div class="nav-inner">
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link to="/products" class="nav-item">全部商品</router-link>
          <router-link to="/activities" class="nav-item">限时活动</router-link>
          <router-link to="/announcements" class="nav-item">商城公告</router-link>
          <router-link to="/recharge" class="nav-item highlight">⚡ 快速充值</router-link>
        </div>
      </nav>
    </header>

    <main class="c-main">
      <router-view />
    </main>

    <footer class="c-footer">
      <div class="footer-inner">
        <p>© 2025 中国移动积分商城 · 仅供演示</p>
        <p class="footer-links">
          <a href="#">使用说明</a> ·
          <a href="#">隐私政策</a> ·
          <a href="#">联系我们</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ShoppingCart } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { authApi } from '@/api/auth'
import { productsApi } from '@/api/products'
import { cartApi } from '@/api/cart'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const keyword = ref('')
const categories = ref<{ id: number; name: string }[]>([])
const hotKeywords = ['手机', '家电', '零食', '护肤品', '运动', '话费充值', '会员']

onMounted(async () => {
  try {
    const res = await productsApi.categories()
    categories.value = res.data?.data ?? []
  } catch {}
  // 加载购物车数量
  if (authStore.isLoggedIn) {
    try {
      const r: any = await cartApi.list()
      const items = r.data?.items || r.data || []
      cartStore.setCount(items.reduce((s: number, i: any) => s + (i.quantity || 1), 0))
    } catch {}
  }
})

function doSearch() {
  if (keyword.value.trim()) {
    router.push({ path: '/products', query: { keyword: keyword.value.trim() } })
  }
}

function quickSearch(kw: string) {
  keyword.value = kw
  router.push({ path: '/products', query: { keyword: kw } })
}

async function handleUserCmd(cmd: string) {
  switch (cmd) {
    case 'profile': router.push('/user'); break
    case 'orders': router.push('/user/orders'); break
    case 'points': router.push('/user/points'); break
    case 'merchant': router.push('/merchant'); break
    case 'admin': router.push('/admin'); break
    case 'logout':
      try { await authApi.logout() } catch {}
      authStore.logout()
      cartStore.reset()
      ElMessage.success('已退出登录')
      router.push('/')
      break
  }
}
</script>

<style scoped lang="scss">
.c-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ---- 顶部信息条 ---- */
.top-bar {
  background: #f5f5f5;
  border-bottom: 1px solid #e8e8e8;
  font-size: 12px;
  color: #888;
}
.top-bar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 6px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.top-bar-welcome { font-size: 12px; color: #999; }
.top-bar-links {
  display: flex;
  align-items: center;
  gap: 8px;
}
.top-link {
  color: #666;
  text-decoration: none;
  font-size: 12px;
  &:hover { color: $primary-color; }
}
.top-divider { color: #ddd; }

/* ---- 主 Header ---- */
.c-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 24px;
}

/* ---- Logo ---- */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary-color, #00c96e);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-texts {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.logo-main {
  font-size: 18px;
  font-weight: 700;
  color: $primary-color;
}
.logo-sub {
  font-size: 11px;
  color: #aaa;
  letter-spacing: 1px;
}

/* ---- 搜索框 ---- */
.search-wrap {
  flex: 1;
  max-width: 560px;
}
.search-bar {
  display: flex;
  border: 2px solid $primary-color;
  border-radius: 4px;
  overflow: hidden;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px 14px;
  font-size: 14px;
  color: #333;
}
.search-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 20px;
  background: $primary-color;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  &:hover { opacity: 0.9; }
}
.hot-search {
  margin-top: 6px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.hot-label { font-size: 12px; color: #aaa; }
.hot-tag {
  font-size: 12px;
  color: #666;
  cursor: pointer;
  &:hover { color: $primary-color; }
}

/* ---- 右侧 ---- */
.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
  margin-left: auto;
}
.cart-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-decoration: none;
  color: #333;
  font-size: 12px;
  &:hover { color: $primary-color; }
}
.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.user-info-mini {
  display: flex;
  flex-direction: column;
  .nickname {
    font-size: 13px;
    font-weight: 600;
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .usr-pts { font-size: 11px; color: $primary-color; }
}

/* ---- 导航条 ---- */
.header-nav { background: $primary-color; position: relative; }
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: stretch;
}
.nav-all-cats {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  background: rgba(0,0,0,0.18);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  min-width: 160px;
}
.cat-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 200px;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  border-radius: 0 0 6px 6px;
  z-index: 200;
  padding: 6px 0;
}
.cat-ditem {
  display: block;
  padding: 9px 16px;
  font-size: 13px;
  color: #333;
  text-decoration: none;
  &:hover { background: #f0f9eb; color: $primary-color; }
}
.nav-item {
  display: inline-flex;
  align-items: center;
  padding: 0 16px;
  height: 42px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
  transition: background 0.2s;
  &:hover, &.router-link-active { background: rgba(255, 255, 255, 0.15); color: #fff; }
  &.highlight { color: #FFE066; font-weight: 600; }
}

/* ---- 主内容 & 底部 ---- */
.c-main { flex: 1; background: #f5f5f5; min-height: 0; }

.c-footer {
  background: #333;
  color: #aaa;
  text-align: center;
  padding: 20px 16px;
  font-size: 13px;
  .footer-links {
    margin-top: 6px;
    a { color: #888; text-decoration: none; &:hover { color: #ccc; } }
  }
}
</style>
