<template>
  <div>
    <div class="page-title">{{ isEdit ? '编辑地址' : '新增地址' }}</div>
    <el-card style="max-width:480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="姓名"><el-input v-model="form.receiver_name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.receiver_phone" /></el-form-item>
        <el-form-item label="省"><el-input v-model="form.province" /></el-form-item>
        <el-form-item label="市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="区/县"><el-input v-model="form.district" /></el-form-item>
        <el-form-item label="详细地址"><el-input v-model="form.detail" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="设为默认"><el-switch v-model="form.is_default" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">保存</el-button>
          <el-button @click="$router.push('/user/addresses')">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const form = ref({ receiver_name: '', receiver_phone: '', province: '', city: '', district: '', detail: '', is_default: false })

onMounted(async () => {
  if (isEdit.value) {
    const r: any = await userApi.addresses()
    const found = (r.data || []).find((a: any) => String(a.id) === String(route.params.id))
    if (found) form.value = { ...found }
  }
})

async function save() {
  saving.value = true
  try {
    if (isEdit.value) await userApi.updateAddress(Number(route.params.id), form.value)
    else await userApi.addAddress(form.value)
    ElMessage.success('保存成功')
    router.push('/user/addresses')
  } finally { saving.value = false }
}
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
</style>

