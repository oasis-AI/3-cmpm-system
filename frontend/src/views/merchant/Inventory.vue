<template>
  <div>
    <div class="page-title">库存管理</div>
    <el-card>
      <el-table :data="skuList" v-loading="loading" style="width:100%">
        <el-table-column label="商品名称" prop="product_name" min-width="160" />
        <el-table-column label="规格" prop="sku_name" width="120" />
        <el-table-column label="积分价" prop="points_price" width="110">
          <template #default="{ row }">{{ row.points_price?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="库存" prop="stock" width="90">
          <template #default="{ row }">
            <span :class="{ low: row.stock < 10, warning: row.stock < 50 && row.stock >= 10 }">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品状态" prop="product_status" width="90">
          <template #default="{ row }"><el-tag :type="row.product_status === 'on_sale' ? 'success' : 'info'" size="small">{{ row.product_status === 'on_sale' ? '上架' : '下架' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { productsApi } from '@/api/products'

const skuList = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const r: any = await productsApi.merchantList({ page: 1, page_size: 100 })
    const products = r.data?.items || r.data || []
    skuList.value = products.flatMap((p: any) =>
      (p.skus?.length ? p.skus : [{ sku_name: '默认', points_price: p.points_price || p.min_points, stock: p.stock ?? 0 }])
        .map((s: any) => ({ product_name: p.name, sku_name: s.sku_name, points_price: s.points_price, stock: s.stock, product_status: p.status }))
    )
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.low { color: #f56c6c; font-weight: 700; }
.warning { color: #e6a23c; font-weight: 600; }
</style>

