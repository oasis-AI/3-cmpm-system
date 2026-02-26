<template>
  <div>
    <div class="page-header">
      <div class="page-title">积分规则</div>
      <el-button type="primary" @click="openDialog()">+ 新增规则</el-button>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column label="规则名称" prop="name" min-width="140" />
        <el-table-column label="类型" prop="type" width="100">
          <template #default="{ row }"><el-tag size="small">{{ row.type }}</el-tag></template>
        </el-table-column>
        <el-table-column label="积分值" prop="points" width="100">
          <template #default="{ row }">{{ row.points?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="描述" prop="description" />
        <el-table-column label="启用" prop="is_active" width="80">
          <template #default="{ row }"><el-switch v-model="row.is_active" @change="toggleRule(row)" /></template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link size="small" @click="openDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑规则' : '新增规则'" width="480px">
      <el-form :model="form" label-width="90px" style="padding-right:20px">
        <el-form-item label="规则名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="register" value="register" />
            <el-option label="exchange" value="exchange" />
            <el-option label="refund" value="refund" />
            <el-option label="recharge" value="recharge" />
          </el-select>
        </el-form-item>
        <el-form-item label="积分值"><el-input-number v-model="form.points" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
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
import { ElMessage } from 'element-plus'
import { pointsApi } from '@/api/points'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const form = ref({ name: '', type: 'register', points: 100, description: '', is_active: true })

async function load() {
  loading.value = true
  try { const r: any = await pointsApi.adminRules(); list.value = r.data?.items || r.data || [] }
  finally { loading.value = false }
}
function openDialog(item?: any) {
  editItem.value = item || null
  form.value = item ? { ...item } : { name: '', type: 'register', points: 100, description: '', is_active: true }
  dialogVisible.value = true
}
async function save() {
  saving.value = true
  try {
    await pointsApi.adminSaveRule(editItem.value?.id, form.value)
    ElMessage.success('保存成功'); dialogVisible.value = false; load()
  } finally { saving.value = false }
}
async function toggleRule(row: any) {
  try { await pointsApi.adminSaveRule(row.id, { is_active: row.is_active }) }
  catch { row.is_active = !row.is_active }
}
onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; }
</style>

