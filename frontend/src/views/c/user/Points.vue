<template>
  <div>
    <div class="page-title">我的积分</div>
    <div class="balance-card">
      <div class="label">当前积分余额</div>
      <div class="balance">{{ balance?.toLocaleString() || '—' }}</div>
    </div>
    <el-card style="margin-top:16px">
      <div class="section-title">积分记录</div>
      <el-table :data="records" v-loading="loading" style="width:100%">
        <el-table-column label="类型" prop="type" width="110">
          <template #default="{ row }"><el-tag :type="row.amount > 0 ? 'success' : 'danger'" size="small">{{ typeLabel(row.type) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="变动积分" width="120">
          <template #default="{ row }"><span :class="row.amount > 0 ? 'plus' : 'minus'">{{ row.amount > 0 ? '+' : '' }}{{ row.amount?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column label="积分余额" prop="balance_after" width="120">
          <template #default="{ row }">{{ row.balance_after?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="说明" prop="remark" />
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="15" v-model:current-page="page" @update:current-page="loadRecords" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { pointsApi } from '@/api/points'

const balance = ref(0)
const records = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const typeMap: Record<string, string> = { register: '注册奖励', exchange: '积分兑换', refund: '退款返还', recharge: '充值', admin: '管理员调整', expire: '积分过期' }
const typeLabel = (t: string) => typeMap[t] || t

async function loadBalance() {
  const r: any = await pointsApi.balance()
  balance.value = r.data?.balance ?? 0
}
async function loadRecords() {
  loading.value = true
  try {
    const r: any = await pointsApi.records({ page: page.value, page_size: 15 })
    records.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}

onMounted(() => { loadBalance(); loadRecords() })
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.balance-card { background: linear-gradient(135deg,#00c55a,#009944); border-radius: 12px; padding: 28px 32px; color: #fff; text-align: center; }
.label { font-size: 14px; opacity: .85; margin-bottom: 8px; }
.balance { font-size: 48px; font-weight: 700; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 12px; }
.plus { color: #00a854; font-weight: 600; }
.minus { color: #f56c6c; font-weight: 600; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 12px; }
</style>

