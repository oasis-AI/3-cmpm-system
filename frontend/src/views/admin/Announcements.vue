<template>
  <div>
    <div class="page-header">
      <div class="page-title">公告管理</div>
      <el-button type="primary" @click="openDialog()">+ 发布公告</el-button>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column label="标题" prop="title" min-width="180" />
        <el-table-column label="类型" prop="type" width="90">
          <template #default="{ row }"><el-tag size="small">{{ row.type || '公告' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="内容摘要" prop="content" min-width="200">
          <template #default="{ row }">{{ row.content?.slice(0, 50) }}{{ row.content?.length > 50 ? '...' : '' }}</template>
        </el-table-column>
        <el-table-column label="发布时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link size="small" @click="openDialog(row)">编辑</el-button>
            <el-button link size="small" type="danger" @click="del(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="10" v-model:current-page="page" @update:current-page="load" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑公告' : '发布公告'" width="540px">
      <el-form :model="form" label-width="80px" style="padding-right:20px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="系统公告" value="system" />
            <el-option label="活动公告" value="activity" />
            <el-option label="促销公告" value="promotion" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="6" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activitiesApi } from '@/api/activities'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const dialogVisible = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const form = ref({ title: '', type: 'system', content: '' })

async function load() {
  loading.value = true
  try {
    const r: any = await activitiesApi.adminAnnouncements.list({ page: page.value, page_size: 10 })
    list.value = r.data?.items || r.data || []; total.value = r.data?.total || 0
  } finally { loading.value = false }
}
function openDialog(item?: any) {
  editItem.value = item || null
  form.value = item ? { title: item.title, type: item.type || 'system', content: item.content } : { title: '', type: 'system', content: '' }
  dialogVisible.value = true
}
async function save() {
  saving.value = true
  try {
    if (editItem.value) await activitiesApi.adminAnnouncements.update(editItem.value.id, form.value)
    else await activitiesApi.adminAnnouncements.create(form.value)
    ElMessage.success('发布成功'); dialogVisible.value = false; load()
  } finally { saving.value = false }
}
async function del(id: number) {
  await ElMessageBox.confirm('确认删除该公告？', '提示', { type: 'warning' })
  await activitiesApi.adminAnnouncements.delete(id)
  ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

