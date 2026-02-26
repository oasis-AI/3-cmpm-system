<template>
  <div>
    <div class="page-title">商户控制台</div>
    <el-row :gutter="16" class="stats-row" v-loading="loading">
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
          <template #header>最新订单</template>
          <el-table :data="recentOrders" style="width:100%">
            <el-table-column label="订单号" prop="order_no" width="160" />
            <el-table-column label="商品" prop="product_name" />
            <el-table-column label="积分" prop="total_points" width="90">
              <template #default="{ row }">{{ row.total_points?.toLocaleString() }}</template>
            </el-table-column>
            <el-table-column label="状态" prop="status" width="80">
              <template #default="{ row }"><el-tag size="small">{{ row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>低库存提醒</template>
          <el-table :data="lowStock" style="width:100%">
            <el-table-column label="商品" prop="product_name" />
            <el-table-column label="规格" prop="sku_name" />
            <el-table-column label="剩余库存" prop="stock" width="90">
              <template #default="{ row }"><span :class="{ danger: row.stock < 10 }">{{ row.stock }}</span></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import { productsApi } from '@/api/products'

const loading = ref(false)
const stats = ref([
  { label: '今日销售额（积分）', value: '—' },
  { label: '本月总销售', value: '—' },
  { label: '待发货订单', value: '—' },
  { label: '在售商品数', value: '—' },
])
const recentOrders = ref<any[]>([])
const lowStock = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [ordR, proR]: any[] = await Promise.all([
      ordersApi.merchantList({ page: 1, page_size: 5 }),
      productsApi.merchantList({ page: 1, page_size: 20 }),
    ])
    recentOrders.value = ordR.data?.items || ordR.data || []
    const products = proR.data?.items || proR.data || []
    stats.value[3].value = String(products.length)
    const pending = recentOrders.value.filter((o: any) => o.status === 'paid').length
    stats.value[2].value = String(pending)
    // low-stock：库存<10 从任意sku里筛
    lowStock.value = products.flatMap((p: any) =>
      (p.skus || []).filter((s: any) => s.stock < 20).map((s: any) => ({ product_name: p.name, sku_name: s.sku_name, stock: s.stock }))
    ).slice(0, 6)
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.stats-row { margin-bottom: 4px; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #00a854; }
.danger { color: #f56c6c; font-weight: 600; }
</style>

