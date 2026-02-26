<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <span class="logo-text">积分商城</span>
        <p class="logo-sub">中国移动积分兑换平台</p>
      </div>

      <el-tabs v-model="activeTab" class="auth-tabs">
        <!-- 密码登录 -->
        <el-tab-pane label="密码登录" name="password">
          <el-form ref="passFormRef" :model="passForm" :rules="passRules" @submit.prevent="loginByPass">
            <el-form-item prop="phone">
              <el-input v-model="passForm.phone" placeholder="手机号" size="large" maxlength="11">
                <template #prefix><el-icon><Phone /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="passForm.password"
                type="password"
                placeholder="密码"
                size="large"
                show-password
              >
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" native-type="submit" style="width:100%">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="auth-footer">
        <span>没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { Phone, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const activeTab = ref('password')
const loading = ref(false)
const passFormRef = ref<FormInstance>()

const passForm = reactive({ phone: '', password: '' })
const passRules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' },
  ],
  password: [{ required: true, message: '请输入密码' }],
}

async function loginByPass() {
  const valid = await passFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res: any = await authApi.login({ phone: passForm.phone, password: passForm.password })
    authStore.setTokens(res.data.access_token, res.data.refresh_token)

    // 拉取用户信息
    const profile: any = await authApi.profile()
    authStore.setUserInfo(profile.data)

    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string
    // 根据角色跳转
    if (profile.data.role === 'admin') {
      router.push(redirect || '/admin')
    } else if (profile.data.role === 'merchant') {
      router.push(redirect || '/merchant')
    } else {
      router.push(redirect || '/')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #00a854 0%, #00c878 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px 48px;
  width: 420px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
}

.auth-logo {
  text-align: center;
  margin-bottom: 28px;
  .logo-text { font-size: 28px; font-weight: 700; color: $primary-color; }
  .logo-sub { font-size: 13px; color: #999; margin-top: 4px; }
}

.auth-tabs { margin-bottom: 8px; }

.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
  a { color: $primary-color; text-decoration: none; }
}
</style>
