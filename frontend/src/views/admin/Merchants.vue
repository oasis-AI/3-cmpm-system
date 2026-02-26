<template>
  <div>
    <div class="page-title">商户管理</div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="statusFilter" clearable placeholder="全部状态" style="width:140px" @change="load(1)">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>
      </div>
      <el-table :data="list" v-loading="loading" style="width:100%;margin-top:12px">
        <el-table-column label="商户名称" prop="merchant_name" min-width="140" />
        <el-table-column label="联系人" prop="contact_name" width="100" />
        <el-table-column label="联系电话" prop="contact_phone" width="130" />
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }"><el-tag :type="tagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="申请时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button link type="success" size="small" @click="review(row.id, 'approved')">通过</el-button>
              <el-button link type="danger" size="small" @click="openReject(row)">拒绝</el-button>
            </template>
            <span v-else class="reviewed">已处理</span>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="15" v-model:current-page="page" @update:current-page="load" />
      </div>
    </el-card>

    <el-dialog v-model="rejectDialog" title="拒绝原因" width="400px">
      <el-input v-model="rejectReason" type="textarea" placeholder="请输入拒绝原因" :rows="4" />
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="doReject" :loading="reviewing">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const statusFilter = ref('')
const rejectDialog = ref(false)
const rejectReason = ref('')
const reviewing = ref(false)
const currentId = ref<number>(0)

const statusMap: Record<string, string> = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
const tagMap: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }
const statusLabel = (s: string) => statusMap[s] || s
const tagType = (s: string) => (tagMap[s] || '') as any

async function load(p?: number) {
  if (p) page.value = p
  loading.value = true
  try {
    const r: any = await request.get('/admin/merchants', { params: { page: page.value, page_size: 15, status: statusFilter.value || undefined } })
    list.value = (r as any).data?.items || (r as any).data || []
    total.value = (r as any).data?.total || 0
  } finally { loading.value = false }
}
async function review(id: number, action: string, reason?: string) {
  reviewing.value = true
  try {
    await request.put(`/admin/merchants/${id}/review`, { action, reason: reason || '' })
    ElMessage.success(action === 'approved' ? '已通过' : '已拒绝'); load()
  } finally { reviewing.value = false }
}
function openReject(row: any) { currentId.value = row.id; rejectReason.value = ''; rejectDialog.value = true }
async function doReject() {
  await review(currentId.value, 'rejected', rejectReason.value)
  rejectDialog.value = false
}
onMounted(() => load())
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
.reviewed { font-size: 13px; color: #bbb; }
</style>

