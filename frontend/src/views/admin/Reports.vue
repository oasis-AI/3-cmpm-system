<template>
  <div>
    <div class="page-title">数据报表</div>
    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card class="stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header>积分流转记录（最新）</template>
          <el-table :data="pointRecords" style="width:100%">
            <el-table-column label="类型" prop="type" width="100">
              <template #default="{ row }"><el-tag :type="row.amount > 0 ? 'success' : 'danger'" size="small">{{ row.type }}</el-tag></template>
            </el-table-column>
            <el-table-column label="变动" prop="amount" width="100">
              <template #default="{ row }"><span :style="{ color: row.amount > 0 ? '#00a854' : '#f56c6c' }">{{ row.amount > 0 ? '+' : '' }}{{ row.amount?.toLocaleString() }}</span></template>
            </el-table-column>
            <el-table-column label="余额" prop="balance_after" width="100">
              <template #default="{ row }">{{ row.balance_after?.toLocaleString() }}</template>
            </el-table-column>
            <el-table-column label="时间" prop="created_at">
              <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>订单统计</template>
          <el-table :data="orderStats" style="width:100%">
            <el-table-column label="状态" prop="label" />
            <el-table-column label="数量" prop="count" width="90" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/user'
import { pointsApi } from '@/api/points'
import { ordersApi } from '@/api/orders'

const loading = ref(false)
const stats = ref([
  { label: '累计用户数', value: '—' },
  { label: '累计积分发放', value: '—' },
  { label: '累计订单量', value: '—' },
  { label: '累计积分消耗', value: '—' },
])
const pointRecords = ref<any[]>([])
const orderStats = ref<{ label: string; count: number }[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [uR, pR, oR]: any[] = await Promise.all([
      userApi.adminList({ page: 1, page_size: 1 }),
      pointsApi.records({ page: 1, page_size: 10 }),
      ordersApi.adminList({ page: 1, page_size: 100 }),
    ])
    stats.value[0].value = String(uR.data?.total || '—')
    pointRecords.value = pR.data?.items || pR.data || []
    const allOrders = oR.data?.items || oR.data || []
    stats.value[2].value = String(oR.data?.total || allOrders.length)
    const statusCounts: Record<string, number> = {}
    allOrders.forEach((o: any) => { statusCounts[o.status] = (statusCounts[o.status] || 0) + 1 })
    orderStats.value = Object.entries(statusCounts).map(([k, v]) => ({ label: k, count: v }))
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #00a854; }
</style>

