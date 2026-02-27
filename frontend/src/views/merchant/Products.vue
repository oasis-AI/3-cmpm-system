<template>
  <div>
    <div class="page-header">
      <div class="page-title">商品管理</div>
      <el-button type="primary" @click="openDialog()">+ 发布商品</el-button>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column label="商品图" width="80">
          <template #default="{ row }"><img :src="row.cover_image || 'https://via.placeholder.com/50'" style="width:50px;height:50px;object-fit:cover;border-radius:6px" /></template>
        </el-table-column>
        <el-table-column label="商品名称" prop="name" min-width="160" />
        <el-table-column label="最低积分" prop="min_points" width="100">
          <template #default="{ row }">{{ row.min_points?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }"><el-tag :type="row.status === 'on_sale' ? 'success' : 'info'" size="small">{{ row.status === 'on_sale' ? '上架' : row.status === 'off_shelf' ? '下架' : '待审核' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="总销量" prop="sales_count" width="90" />
        <el-table-column label="创建时间" prop="created_at" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link size="small" @click="openDialog(row)">编辑</el-button>
            <el-button link size="small" type="warning" @click="toggle(row)">{{ row.status === 'on_sale' ? '下架' : '上架' }}</el-button>
            <el-button link size="small" type="danger" @click="del(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="10" v-model:current-page="page" @update:current-page="load" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑商品' : '发布商品'" width="600px">
      <el-form :model="form" label-width="90px" style="padding-right:20px">
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图URL"><el-input v-model="form.cover_image" /></el-form-item>
        <el-form-item label="积分价格"><el-input-number v-model="form.points_price" :min="1" /></el-form-item>
        <el-form-item label="品牌"><el-input v-model="form.brand" /></el-form-item>
        <el-form-item label="商品描述"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productsApi } from '@/api/products'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const dialogVisible = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const categories = ref<any[]>([])
const form = ref({ name: '', category_id: null as number | null, cover_image: '', points_price: 100, brand: '', description: '' })

async function load() {
  loading.value = true
  try {
    const r: any = await productsApi.merchantList({ page: page.value, page_size: 10 })
    list.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}
function openDialog(item?: any) {
  editItem.value = item || null
  form.value = item
    ? { name: item.name, category_id: item.category_id || null, cover_image: item.cover_image, points_price: item.points_price || item.min_points, brand: item.brand, description: item.description }
    : { name: '', category_id: null, cover_image: '', points_price: 100, brand: '', description: '' }
  dialogVisible.value = true
}
async function save() {
  saving.value = true
  try {
    if (editItem.value) await productsApi.update(editItem.value.id, form.value)
    else await productsApi.create(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false; load()
  } finally { saving.value = false }
}
async function toggle(row: any) {
  const newStatus = row.status === 'on_sale' ? 'off_shelf' : 'on_sale'
  await productsApi.toggleStatus(row.id, newStatus)
  ElMessage.success('状态已更新'); load()
}
async function del(id: number) {
  await ElMessageBox.confirm('确认删除该商品？', '提示', { type: 'warning' })
  await productsApi.delete(id); ElMessage.success('已删除'); load()
}
async function loadCategories() {
  try {
    const r: any = await productsApi.categories()
    categories.value = r.data || []
  } catch {}
}
onMounted(() => { load(); loadCategories() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

