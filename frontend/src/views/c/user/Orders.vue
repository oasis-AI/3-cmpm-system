<template>
  <div>
    <div class="page-title">我的订单</div>
    <el-tabs v-model="activeTab" @tab-change="load">
      <el-tab-pane label="全部" name="" />
      <el-tab-pane label="待支付" name="pending" />
      <el-tab-pane label="已支付" name="paid" />
      <el-tab-pane label="已发货" name="shipped" />
      <el-tab-pane label="已完成" name="completed" />
      <el-tab-pane label="已取消" name="cancelled" />
    </el-tabs>

    <div v-loading="loading" style="min-height:200px">
      <el-empty v-if="!loading && !orders.length" description="暂无订单" />
      <div v-for="o in orders" :key="o.id" class="order-card">
        <div class="order-header">
          <span class="order-no">订单号：{{ o.order_no }}</span>
          <el-tag :type="statusTag(o.status)" size="small">{{ statusLabel(o.status) }}</el-tag>
        </div>
        <div class="order-item-row" v-for="item in (o.items || []).slice(0, 1)" :key="item.id">
          <img :src="item.cover_image || 'https://via.placeholder.com/60'" class="item-img" />
          <div class="item-info">
            <div>{{ item.product_name }}</div>
            <div class="item-sub">{{ item.sku_name }}</div>
            <div class="item-pts">{{ item.points_price?.toLocaleString() }} 积分 × {{ item.quantity }}</div>
          </div>
          <div class="item-total">{{ o.total_points?.toLocaleString() }} 积分</div>
        </div>
        <div class="order-footer">
          <span class="order-time">{{ o.created_at?.slice(0, 16) }}</span>
          <div class="action-btns">
            <el-button v-if="o.status === 'pending'" size="small" type="danger" plain @click="cancelOrder(o.id)">取消订单</el-button>
            <el-button v-if="o.status === 'shipped'" size="small" type="primary" @click="confirmOrder(o.id)">确认收货</el-button>
          </div>
        </div>
      </div>
    </div>
    <div class="pagination-wrap">
      <el-pagination background layout="prev,pager,next" :total="total" :page-size="10" v-model:current-page="page" @update:current-page="load" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ordersApi } from '@/api/orders'

const orders = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('')
const page = ref(1)
const total = ref(0)

const statusMap: Record<string, string> = { pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
const tagMap: Record<string, string> = { pending: 'warning', paid: 'success', shipped: '', completed: 'info', cancelled: 'danger' }
const statusLabel = (s: string) => statusMap[s] || s
const statusTag = (s: string) => (tagMap[s] ?? '') as any

async function load() {
  loading.value = true
  try {
    const r: any = await ordersApi.list({ page: page.value, page_size: 10, status: activeTab.value || undefined })
    orders.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}

async function cancelOrder(id: number) {
  await ElMessageBox.confirm('确认取消该订单？', '提示', { type: 'warning' })
  await ordersApi.cancel(id)
  ElMessage.success('已取消')
  load()
}
async function confirmOrder(id: number) {
  await ElMessageBox.confirm('确认已收货？', '提示', { type: 'warning' })
  await ordersApi.confirm(id)
  ElMessage.success('已确认收货')
  load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.order-card { background: #fff; border-radius: 8px; margin-bottom: 12px; overflow: hidden; border: 1px solid #f0f0f0; }
.order-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #fafafa; border-bottom: 1px solid #f0f0f0; }
.order-no { font-size: 13px; color: #888; }
.order-item-row { display: flex; align-items: center; gap: 14px; padding: 14px 16px; }
.item-img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
.item-info { flex: 1; font-size: 14px; }
.item-sub { font-size: 13px; color: #888; }
.item-pts { font-size: 13px; color: #888; margin-top: 4px; }
.item-total { font-weight: 600; color: #f60; }
.order-footer { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-top: 1px solid #f0f0f0; }
.order-time { font-size: 12px; color: #bbb; }
.action-btns { display: flex; gap: 8px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

