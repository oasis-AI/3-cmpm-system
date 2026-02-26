<template>
  <div>
    <div class="page-title">用户管理</div>
    <el-card>
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索手机号或昵称" clearable style="width:220px" @keyup.enter="load(1)" />
        <el-button type="primary" @click="load(1)">搜索</el-button>
      </div>
      <el-table :data="list" v-loading="loading" style="width:100%;margin-top:12px">
        <el-table-column label="ID" prop="id" width="70" />
        <el-table-column label="手机号" prop="phone" width="130" />
        <el-table-column label="昵称" prop="nickname" />
        <el-table-column label="积分余额" prop="points_balance" width="110">
          <template #default="{ row }">{{ row.points_balance?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status === 'active' ? '正常' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="注册时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link :type="row.status === 'active' ? 'danger' : 'primary'" size="small" @click="toggleStatus(row)">{{ row.status === 'active' ? '禁用' : '启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="15" v-model:current-page="page" @update:current-page="load" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'
import request from '@/api/request'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const search = ref('')

async function load(p?: number) {
  if (p) page.value = p
  loading.value = true
  try {
    const r: any = await userApi.adminList({ page: page.value, page_size: 15, keyword: search.value || undefined })
    list.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}
async function toggleStatus(row: any) {
  const newStatus = row.status === 'active' ? 'disabled' : 'active'
  await request.put(`/admin/users/${row.id}/status`, { status: newStatus })
  ElMessage.success('状态已更新'); load()
}
onMounted(() => load())
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

