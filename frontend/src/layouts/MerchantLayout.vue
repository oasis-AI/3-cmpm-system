<template>
  <div class="b-layout">
    <!-- 侧边栏 -->
    <aside class="b-sidebar" :class="{ collapsed }">
      <div class="sidebar-logo" @click="router.push('/merchant')">
        <el-icon size="24"><Shop /></el-icon>
        <span v-if="!collapsed" class="logo-text">商家后台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        background-color="#001529"
        text-color="#ffffffa0"
        active-text-color="#ffffff"
        router
      >
        <el-menu-item index="/merchant/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>概览</template>
        </el-menu-item>
        <el-menu-item index="/merchant/products">
          <el-icon><Goods /></el-icon>
          <template #title>商品管理</template>
        </el-menu-item>
        <el-menu-item index="/merchant/inventory">
          <el-icon><Box /></el-icon>
          <template #title>库存管理</template>
        </el-menu-item>
        <el-menu-item index="/merchant/orders">
          <el-icon><List /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>
        <el-menu-item index="/merchant/analytics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        <el-menu-item index="/merchant/activities">
          <el-icon><Promotion /></el-icon>
          <template #title>活动管理</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-tooltip :content="collapsed ? '返回商城' : ''" placement="right">
          <router-link to="/" class="back-link">
            <el-icon><Back /></el-icon>
            <span v-if="!collapsed">返回商城</span>
          </router-link>
        </el-tooltip>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="b-container">
      <!-- 顶部栏 -->
      <header class="b-topbar">
        <el-button :icon="collapsed ? Expand : Fold" text @click="collapsed = !collapsed" />
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/merchant/dashboard' }">商家后台</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="topbar-right">
          <span class="merchant-name">{{ authStore.userInfo?.nickname }}</span>
          <el-button text @click="handleLogout">退出</el-button>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="b-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Shop, DataBoard, Goods, Box, List, TrendCharts, Promotion,
  Back, Fold, Expand,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)

const titleMap: Record<string, string> = {
  '/merchant/dashboard': '概览',
  '/merchant/products': '商品管理',
  '/merchant/inventory': '库存管理',
  '/merchant/orders': '订单管理',
  '/merchant/analytics': '数据分析',
  '/merchant/activities': '活动管理',
}
const currentTitle = computed(() => titleMap[route.path] || '')

async function handleLogout() {
  try { await authApi.logout() } catch {}
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped lang="scss">
.b-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.b-sidebar {
  width: 220px;
  background: #001529;
  display: flex;
  flex-direction: column;
  transition: width 0.25s;
  flex-shrink: 0;

  &.collapsed { width: 64px; }
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding: 0 16px;
  overflow: hidden;
  white-space: nowrap;
}

.el-menu {
  border-right: none;
  flex: 1;
}

.sidebar-footer {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding: 12px 16px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 13px;
  &:hover { color: #fff; }
}

.b-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.b-topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;

  .el-breadcrumb { flex: 1; }

  .topbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    .merchant-name { font-size: 14px; color: #666; }
  }
}

.b-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f0f2f5;
}
</style>
