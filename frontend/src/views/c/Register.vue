<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <span class="logo-text">积分商城</span>
        <p class="logo-sub">注册享 500 积分大礼包</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
        <el-form-item prop="phone">
          <el-input v-model="form.phone" placeholder="手机号" size="large" maxlength="11">
            <template #prefix><el-icon><Phone /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-form-item prop="sms_code">
          <el-input v-model="form.sms_code" placeholder="短信验证码" size="large" maxlength="6">
            <template #prefix><el-icon><Message /></el-icon></template>
            <template #append>
              <el-button :disabled="countdown > 0" @click="sendSms">
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="设置密码（6-20位）" size="large" show-password>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-button type="primary" size="large" :loading="loading" native-type="submit" style="width:100%">
          立即注册
        </el-button>
      </el-form>

      <div class="auth-footer">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { Phone, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const countdown = ref(0)
const formRef = ref<FormInstance>()

const form = reactive({ phone: '', sms_code: '', password: '' })
const rules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' },
  ],
  sms_code: [{ required: true, message: '请输入验证码' }, { len: 6, message: '验证码为6位数字' }],
  password: [
    { required: true, message: '请设置密码' },
    { min: 6, max: 20, message: '密码长度 6-20 位' },
  ],
}

async function sendSms() {
  if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }
  await authApi.sendSms(form.phone)
  ElMessage.success('验证码已发送（演示：123456）')
  countdown.value = 60
  const t = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(t)
  }, 1000)
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res: any = await authApi.register(form)
    authStore.setTokens(res.data.access_token, res.data.refresh_token)
    const profile: any = await authApi.profile()
    authStore.setUserInfo(profile.data)
    ElMessage.success('注册成功，已赠送 500 积分 🎉')
    router.push('/')
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
.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
  a { color: $primary-color; text-decoration: none; }
}
</style>
