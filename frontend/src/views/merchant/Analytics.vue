<template>
  <div>
    <div class="page-title">数据统计</div>
    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card class="stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:16px">
      <template #header>近期销售商品 Top10</template>
      <el-table :data="topProducts" style="width:100%">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column label="商品名称" prop="name" />
        <el-table-column label="总销量" prop="sales_count" width="100" />
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }"><el-tag :type="row.status === 'on_sale' ? 'success' : 'info'" size="small">{{ row.status === 'on_sale' ? '上架' : '下架' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { productsApi } from '@/api/products'
import { ordersApi } from '@/api/orders'

const loading = ref(false)
const stats = ref([
  { label: '商品总数', value: '—' },
  { label: '总销量', value: '—' },
  { label: '待发货', value: '—' },
  { label: '已完成订单', value: '—' },
])
const topProducts = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [pR, oR]: any[] = await Promise.all([
      productsApi.merchantList({ page: 1, page_size: 100 }),
      ordersApi.merchantList({ page: 1, page_size: 100 }),
    ])
    const products = pR.data?.items || pR.data || []
    const orders = oR.data?.items || oR.data || []
    stats.value[0].value = String(products.length)
    stats.value[1].value = products.reduce((s: number, p: any) => s + (p.sales_count || 0), 0).toLocaleString()
    stats.value[2].value = String(orders.filter((o: any) => o.status === 'paid').length)
    stats.value[3].value = String(orders.filter((o: any) => o.status === 'completed').length)
    topProducts.value = [...products].sort((a, b) => (b.sales_count || 0) - (a.sales_count || 0)).slice(0, 10)
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #00a854; }
</style>

