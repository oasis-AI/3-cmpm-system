<template>
  <div class="c-layout">
    <header class="c-header">
      <div class="header-inner">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <span class="logo-text">积分商城</span>
        </router-link>

        <!-- 搜索框 -->
        <div class="search-bar">
          <el-input
            v-model="keyword"
            placeholder="搜索商品、礼品..."
            clearable
            @keyup.enter="doSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="doSearch" />
            </template>
          </el-input>
        </div>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 快速充值 -->
          <router-link to="/recharge" class="action-link">
            <el-icon><Phone /></el-icon> 话费充值
          </router-link>

          <!-- 购物车 -->
          <router-link to="/cart" class="action-link cart-link">
            <el-badge :value="cartStore.count || ''" :hidden="!cartStore.count">
              <el-icon size="20"><ShoppingCart /></el-icon>
            </el-badge>
            <span>购物车</span>
          </router-link>

          <!-- 用户 -->
          <template v-if="authStore.isLoggedIn">
            <el-dropdown @command="handleUserCmd">
              <span class="user-trigger">
                <el-avatar :size="32" :src="authStore.userInfo?.avatar" />
                <span class="nickname">{{ authStore.userInfo?.nickname }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                  <el-dropdown-item command="points">积分明细</el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isMerchant" command="merchant" divided>
                    商家后台
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" command="admin" divided>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="action-link">登录</router-link>
            <router-link to="/register" class="action-link">注册</router-link>
          </template>
        </div>
      </div>

      <!-- 导航条 -->
      <nav class="header-nav">
        <div class="nav-inner">
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link to="/products" class="nav-item">全部商品</router-link>
          <router-link
            v-for="cat in categories"
            :key="cat.id"
            :to="{ path: '/products', query: { category_id: cat.id } }"
            class="nav-item"
          >{{ cat.name }}</router-link>
          <router-link to="/activities" class="nav-item">限时活动</router-link>
          <router-link to="/recharge" class="nav-item highlight">快速充值</router-link>
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
import { Search, Phone, ShoppingCart } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { authApi } from '@/api/auth'
import { productsApi } from '@/api/products'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const keyword = ref('')
const categories = ref<{ id: number; name: string }[]>([])

onMounted(async () => {
  try {
    const res = await productsApi.categories()
    categories.value = res.data?.data ?? []
  } catch {}
})

function doSearch() {
  if (keyword.value.trim()) {
    router.push({ path: '/products', query: { keyword: keyword.value.trim() } })
  }
}

async function handleUserCmd(cmd: string) {
  switch (cmd) {
    case 'profile': router.push('/user/profile'); break
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
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;

  img { height: 36px; }
  .logo-text {
    font-size: 20px;
    font-weight: 700;
    color: $primary-color;
  }
}

.search-bar {
  flex: 1;
  max-width: 520px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
  margin-left: auto;
}

.action-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;

  &:hover { color: $primary-color; }
}

.cart-link { position: relative; }

.user-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;

  .nickname {
    font-size: 14px;
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.header-nav {
  background: $primary-color;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
}

.nav-item {
  display: inline-block;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
  transition: background 0.2s;

  &:hover, &.router-link-active { background: rgba(255, 255, 255, 0.15); color: #fff; }
  &.highlight { color: #FFE066; font-weight: 600; }
}

.c-main {
  flex: 1;
  background: #f5f5f5;
  min-height: 0;
}

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
