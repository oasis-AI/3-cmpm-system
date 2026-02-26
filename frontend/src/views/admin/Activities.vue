<template>
  <div>
    <div class="page-header">
      <div class="page-title">活动管理</div>
      <el-button type="primary" @click="openDialog()">+ 创建活动</el-button>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column label="活动名称" prop="title" min-width="180" />
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }"><el-tag :type="tagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="开始时间" prop="start_time" width="160">
          <template #default="{ row }">{{ row.start_time?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="结束时间" prop="end_time" width="160">
          <template #default="{ row }">{{ row.end_time?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link size="small" @click="openDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑活动' : '创建活动'" width="520px">
      <el-form :model="form" label-width="90px" style="padding-right:20px">
        <el-form-item label="活动名称"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="开始时间"><el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" /></el-form-item>
        <el-form-item label="结束时间"><el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" /></el-form-item>
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
import { activitiesApi } from '@/api/activities'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const form = ref({ title: '', description: '', start_time: '', end_time: '' })

const statusMap: Record<string, string> = { active: '进行中', pending: '未开始', ended: '已结束' }
const tagMap: Record<string, string> = { active: 'success', pending: 'warning', ended: 'info' }
const statusLabel = (s: string) => statusMap[s] || s
const tagType = (s: string) => (tagMap[s] || '') as any

async function load() {
  loading.value = true
  try { const r: any = await activitiesApi.list(); list.value = r.data?.items || r.data || [] }
  finally { loading.value = false }
}
function openDialog(item?: any) {
  editItem.value = item || null
  form.value = item ? { title: item.title, description: item.description, start_time: item.start_time, end_time: item.end_time } : { title: '', description: '', start_time: '', end_time: '' }
  dialogVisible.value = true
}
async function save() {
  saving.value = true
  try {
    if (editItem.value) await activitiesApi.adminUpdate(editItem.value.id, form.value)
    else await activitiesApi.adminCreate(form.value)
    ElMessage.success('保存成功'); dialogVisible.value = false; load()
  } finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; }
</style>

