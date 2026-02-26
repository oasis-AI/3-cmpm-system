<template>
  <div>
    <div class="page-title">个人信息</div>
    <el-card class="profile-card">
      <el-form :model="form" label-width="100px" style="max-width:480px">
        <el-form-item label="头像">
          <el-avatar :size="64" :src="form.avatar" icon="UserFilled" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
            <el-radio :label="0">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="pwd-card" style="margin-top:16px">
      <div class="section-title">修改密码</div>
      <el-form :model="pwdForm" label-width="100px" style="max-width:480px">
        <el-form-item label="当前密码"><el-input v-model="pwdForm.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
        <el-form-item label="确认新密码"><el-input v-model="pwdForm.confirm" type="password" show-password /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePwd" :loading="changingPwd">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { userApi } from '@/api/user'


const authStore = useAuthStore()
const saving = ref(false)
const changingPwd = ref(false)
const form = ref({ phone: '', nickname: '', gender: 0, avatar: '' })
const pwdForm = ref({ old_password: '', new_password: '', confirm: '' })

onMounted(async () => {
  const r: any = await authApi.profile()
  const u = r.data
  form.value = { phone: u.phone, nickname: u.nickname || '', gender: u.gender ?? 0, avatar: u.avatar || '' }
})

async function save() {
  saving.value = true
  try {
    await userApi.updateProfile({ nickname: form.value.nickname })
    ElMessage.success('保存成功')
  } finally { saving.value = false }
}

async function changePwd() {
  if (pwdForm.value.new_password !== pwdForm.value.confirm) { ElMessage.error('两次密码不一致'); return }
  changingPwd.value = true
  try {
    await userApi.changePassword({ old_password: pwdForm.value.old_password, new_password: pwdForm.value.new_password })
    ElMessage.success('密码已修改，请重新登录')
    authStore.logout()
  } finally { changingPwd.value = false }
}
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
</style>

