<template>
  <div>
    <div class="page-title">管理控制台</div>
    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card class="stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" :style="{ color: s.color || '#00a854' }">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header>待审核商户</template>
          <el-table :data="pendingMerchants" style="width:100%">
            <el-table-column label="商户名称" prop="merchant_name" />
            <el-table-column label="联系人" prop="contact_name" />
            <el-table-column label="申请时间" prop="created_at" width="120">
              <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="$router.push('/admin/merchants')">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最新注册用户</template>
          <el-table :data="recentUsers" style="width:100%">
            <el-table-column label="手机号" prop="phone" />
            <el-table-column label="昵称" prop="nickname" />
            <el-table-column label="积分" prop="points_balance" width="90">
              <template #default="{ row }">{{ row.points_balance?.toLocaleString() }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/user'
import request from '@/api/request'

const loading = ref(false)
const stats = ref([
  { label: '总用户数', value: '—', color: '#00a854' },
  { label: '今日新增用户', value: '—', color: '#409eff' },
  { label: '待审核商户', value: '—', color: '#e6a23c' },
  { label: '平台总积分流转', value: '—', color: '#f56c6c' },
])
const pendingMerchants = ref<any[]>([])
const recentUsers = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [uR, mR]: any[] = await Promise.all([
      userApi.adminList({ page: 1, page_size: 5 }),
      request.get('/admin/merchants', { params: { page: 1, page_size: 5, status: 'pending' } }),
    ])
    recentUsers.value = uR.data?.items || uR.data || []
    stats.value[0].value = String(uR.data?.total || recentUsers.value.length)
    const merchants = (mR as any).data?.items || (mR as any).data || []
    pendingMerchants.value = merchants
    stats.value[2].value = String((mR as any).data?.total || merchants.length)
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; }
</style>

