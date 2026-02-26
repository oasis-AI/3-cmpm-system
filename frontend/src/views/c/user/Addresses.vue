<template>
  <div>
    <div class="page-header">
      <div class="page-title">收货地址</div>
      <el-button type="primary" @click="openDialog()">+ 新增地址</el-button>
    </div>

    <div v-loading="loading" style="min-height:100px">
      <el-empty v-if="!loading && !list.length" description="暂无地址" />
      <div v-for="a in list" :key="a.id" class="addr-card">
        <div class="addr-main">
          <div class="name-row">
            <span class="name">{{ a.receiver_name }}</span>
            <span class="phone">{{ a.receiver_phone }}</span>
            <el-tag v-if="a.is_default" size="small" type="success" style="margin-left:8px">默认</el-tag>
          </div>
          <div class="addr-text">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</div>
        </div>
        <div class="addr-actions">
          <el-button link @click="openDialog(a)">编辑</el-button>
          <el-button link type="danger" @click="del(a.id)">删除</el-button>
          <el-button v-if="!a.is_default" link type="primary" @click="setDefault(a.id)">设为默认</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑地址' : '新增地址'" width="500px">
      <el-form :model="form" label-width="90px" style="padding-right:20px">
        <el-form-item label="姓名"><el-input v-model="form.receiver_name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.receiver_phone" /></el-form-item>
        <el-form-item label="省"><el-input v-model="form.province" /></el-form-item>
        <el-form-item label="市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="区/县"><el-input v-model="form.district" /></el-form-item>
        <el-form-item label="详细地址"><el-input v-model="form.detail" type="textarea" /></el-form-item>
        <el-form-item label="设为默认"><el-switch v-model="form.is_default" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api/user'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const form = ref({ receiver_name: '', receiver_phone: '', province: '', city: '', district: '', detail: '', is_default: false })

async function load() {
  loading.value = true
  try { const r: any = await userApi.addresses(); list.value = r.data || [] }
  finally { loading.value = false }
}
function openDialog(item?: any) {
  editItem.value = item || null
  form.value = item ? { ...item } : { receiver_name: '', receiver_phone: '', province: '', city: '', district: '', detail: '', is_default: false }
  dialogVisible.value = true
}
async function save() {
  saving.value = true
  try {
    if (editItem.value) await userApi.updateAddress(editItem.value.id, form.value)
    else await userApi.addAddress(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally { saving.value = false }
}
async function del(id: number) {
  await ElMessageBox.confirm('确认删除该地址？', '提示', { type: 'warning' })
  await userApi.deleteAddress(id)
  ElMessage.success('已删除')
  load()
}
async function setDefault(id: number) {
  const item = list.value.find((a: any) => a.id === id)
  if (!item) return
  await userApi.updateAddress(id, { ...item, is_default: 1 })
  ElMessage.success('已设为默认')
  load()
}
onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; }
.addr-card { background: #fff; border: 1px solid #f0f0f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
.name-row { display: flex; align-items: center; margin-bottom: 6px; }
.name { font-weight: 600; margin-right: 10px; }
.phone { color: #888; font-size: 13px; }
.addr-text { font-size: 13px; color: #666; }
.addr-actions { display: flex; gap: 4px; flex-shrink: 0; }
</style>

