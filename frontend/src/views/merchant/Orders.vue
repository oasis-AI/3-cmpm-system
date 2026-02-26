<template>
  <div>
    <div class="page-title">订单管理</div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="statusFilter" clearable placeholder="全部状态" style="width:140px" @change="load">
          <el-option label="待支付" value="pending" />
          <el-option label="已支付" value="paid" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
      <el-table :data="list" v-loading="loading" style="width:100%;margin-top:12px">
        <el-table-column label="订单号" prop="order_no" width="180" />
        <el-table-column label="商品" prop="product_name" />
        <el-table-column label="数量" prop="quantity" width="70" />
        <el-table-column label="积分" prop="total_points" width="110">
          <template #default="{ row }">{{ row.total_points?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="收货人" prop="receiver_name" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><el-tag :type="tagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="下单时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button v-if="row.status === 'paid'" link type="primary" size="small" @click="shipOrder(row)">发货</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="10" v-model:current-page="page" @update:current-page="load" />
      </div>
    </el-card>

    <el-dialog v-model="shipDialog" title="填写发货信息" width="420px">
      <el-form :model="shipForm" label-width="90px">
        <el-form-item label="快递公司"><el-input v-model="shipForm.company" placeholder="如：顺丰、京东快递" /></el-form-item>
        <el-form-item label="运单号"><el-input v-model="shipForm.tracking_no" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmShip" :loading="shipping">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ordersApi } from '@/api/orders'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const statusFilter = ref('')
const shipDialog = ref(false)
const shipping = ref(false)
const currentOrder = ref<any>(null)
const shipForm = ref({ company: '', tracking_no: '' })

const statusMap: Record<string, string> = { pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
const tagMap: Record<string, string> = { pending: 'warning', paid: 'success', shipped: '', completed: 'info', cancelled: 'danger' }
const statusLabel = (s: string) => statusMap[s] || s
const tagType = (s: string) => (tagMap[s] || '') as any

async function load() {
  loading.value = true
  try {
    const r: any = await ordersApi.merchantList({ page: page.value, page_size: 10, status: statusFilter.value || undefined })
    list.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}
function shipOrder(order: any) {
  currentOrder.value = order
  shipForm.value = { company: '', tracking_no: '' }
  shipDialog.value = true
}
async function confirmShip() {
  if (!shipForm.value.tracking_no) { ElMessage.warning('请填写运单号'); return }
  shipping.value = true
  try {
    await ordersApi.ship(currentOrder.value.id, shipForm.value)
    ElMessage.success('发货成功')
    shipDialog.value = false; load()
  } finally { shipping.value = false }
}
onMounted(load)
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

