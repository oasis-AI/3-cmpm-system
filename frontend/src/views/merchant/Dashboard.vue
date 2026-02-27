<template>
  <div class="dashboard">
    <div class="page-header">
      <h2 class="page-title">商户控制台</h2>
      <span class="page-sub">欢迎回来，{{ authStore.userInfo?.nickname }}</span>
    </div>

    <!-- 低库存预警横幅 -->
    <el-alert
      v-if="lowStockCount > 0"
      :title="`库存预警：有 ${lowStockCount} 个 SKU 库存不足 10 件`"
      type="warning"
      show-icon
      :closable="false"
      class="alert-bar"
    >
      <template #default>
        <el-button size="small" type="warning" plain @click="$router.push('/merchant/inventory')">查看库存</el-button>
      </template>
    </el-alert>

    <!-- 数据卡片 -->
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-icon" :style="{ background: s.bg }">
          <el-icon :size="22" :color="s.color"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
        </div>
      </div>
    </div>

    <!-- 下半区 -->
    <div class="bottom-grid">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">最新订单</span>
          <el-button link type="primary" size="small" @click="$router.push('/merchant/orders')">查看全部</el-button>
        </div>
        <el-table :data="recentOrders" style="width:100%" :show-header="true" size="small">
          <el-table-column label="订单号" prop="order_no" width="150" />
          <el-table-column label="商品" prop="product_name" show-overflow-tooltip />
          <el-table-column label="积分" width="90">
            <template #default="{ row }">{{ row.total_points?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small" round>{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!recentOrders.length && !loading" description="暂无订单" :image-size="60" />
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">库存预警</span>
          <el-button link type="primary" size="small" @click="$router.push('/merchant/inventory')">管理库存</el-button>
        </div>
        <el-table :data="lowStock" style="width:100%" size="small">
          <el-table-column label="商品" prop="product_name" show-overflow-tooltip />
          <el-table-column label="规格" prop="sku_name" show-overflow-tooltip />
          <el-table-column label="剩余" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.stock < 5 ? 'danger' : 'warning'" size="small" round>{{ row.stock }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!lowStock.length && !loading" description="库存充足" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import { productsApi } from '@/api/products'
import { useAuthStore } from '@/stores/auth'
import { TrendCharts, List, Goods, Warning } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const loading = ref(false)
const stats = ref([
  { label: '今日销售额（积分）', value: '—', icon: TrendCharts, color: '#00a854', bg: '#e8f5ee' },
  { label: '本月总销售', value: '—', icon: TrendCharts, color: '#1890ff', bg: '#e3f2fd' },
  { label: '待发货订单', value: '—', icon: List, color: '#ff6600', bg: '#fff3e0' },
  { label: '在售商品数', value: '—', icon: Goods, color: '#9c27b0', bg: '#f3e5f5' },
])
const recentOrders = ref<any[]>([])
const lowStock = ref<any[]>([])
const lowStockCount = ref(0)

const statusText = (s: string) => ({ pending:'待支付', paid:'待发货', shipped:'已发货', completed:'已完成', cancelled:'已取消' }[s] || s)
const statusType = (s: string) => ({ pending:'info', paid:'warning', shipped:'primary', completed:'success', cancelled:'danger' }[s] || '')

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
    const allLowStock = products.flatMap((p: any) =>
      (p.skus || []).filter((s: any) => (s.stock ?? 99) < 10).map((s: any) => ({ product_name: p.name, sku_name: s.sku_name, stock: s.stock ?? 0 }))
    )
    lowStockCount.value = allLowStock.length
    lowStock.value = allLowStock.slice(0, 6)
  } finally { loading.value = false }
})
</script>

<style scoped lang="scss">
.dashboard { padding: 0; }

.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #222;
  margin: 0;
}
.page-sub { font-size: 13px; color: #999; }

.alert-bar { margin-bottom: 20px; border-radius: 10px; }

/* 数据卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: transform .2s, box-shadow .2s;
  &:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.09); }
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-label { font-size: 12px; color: #999; margin-bottom: 6px; }
.stat-value { font-size: 26px; font-weight: 700; line-height: 1; }

/* 下半部分 */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.panel {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #222;
}
</style>

