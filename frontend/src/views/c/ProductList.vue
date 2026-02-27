<template>
  <div class="product-list-page">
    <div class="layout-container">
      <!-- 分类侧边栏 -->
      <aside class="category-sidebar">
        <div class="cat-item cat-item-all" :class="{ active: !selectedCat }" @click="selectCat(null)">全部商品</div>
        <div class="cat-divider"></div>
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="cat-item"
          :class="{ active: selectedCat === cat.id }"
          @click="selectCat(cat.id)"
        >{{ cat.name }}</div>
      </aside>

      <main class="product-main">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="keyword"
            placeholder="搜索商品"
            clearable
            style="width:240px"
            @keyup.enter="doSearch"
            @clear="doSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="sort" style="width:150px;margin-left:12px" @change="doSearch">
            <el-option label="默认排序" value="default" />
            <el-option label="积分从低到高" value="points_asc" />
            <el-option label="积分从高到低" value="points_desc" />
            <el-option label="销量优先" value="sales" />
          </el-select>
          <span class="result-count" v-if="total > 0">共 {{ total }} 件</span>
        </div>

        <!-- 商品网格 -->
        <div v-loading="loading" class="product-grid" style="min-height:200px">
          <div
            v-for="p in products"
            :key="p.id"
            class="product-card"
            @click="$router.push(`/products/${p.id}`)"
          >
            <img :src="p.cover_image || 'https://via.placeholder.com/200'" class="product-img" />
            <div class="product-info">
              <div class="product-name">{{ p.name }}</div>
              <div class="product-tags" v-if="p.tags">
                <el-tag v-for="t in p.tags.split(',')" :key="t" size="small" style="margin-right:4px">{{ t.trim() }}</el-tag>
              </div>
              <div class="product-price">
                <span class="points">{{ (p.points_price || 0).toLocaleString() }}</span>
                <span class="unit">积分起</span>
              </div>
              <div class="product-sales">已兑换 {{ p.sales_count || 0 }} 件</div>
            </div>
          </div>
          <el-empty v-if="!loading && products.length === 0" description="暂无商品" style="width:100%" />
        </div>

        <!-- 分页 -->
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            background
            layout="prev, pager, next"
            @current-change="fetchProducts"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { productsApi } from '@/api/products'

const route = useRoute()
const router = useRouter()
const categories = ref<any[]>([])
const products = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const selectedCat = ref<number | null>(null)
const keyword = ref('')
const sort = ref('default')

// 当路由 query 变化时（如首页点击分类导航）重新加载
watch(() => route.query, (q) => {
  keyword.value = String(q.keyword || '')
  if (q.category_id) selectedCat.value = Number(q.category_id)
  fetchProducts()
}, { immediate: false })

onMounted(async () => {
  const r = await productsApi.categories()
  categories.value = (r as any).data || []
  // 处理 URL query 参数
  keyword.value = String(route.query.keyword || '')
  if (route.query.category_id) selectedCat.value = Number(route.query.category_id)
  fetchProducts()
})

async function fetchProducts() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize }
    if (selectedCat.value) params.category_id = selectedCat.value
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (sort.value !== 'default') params.sort = sort.value
    const r: any = await productsApi.list(params)
    products.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally {
    loading.value = false
  }
}

function selectCat(id: number | null) {
  selectedCat.value = id
  page.value = 1
  router.replace({ query: { ...(id ? { category_id: id } : {}), ...(keyword.value ? { keyword: keyword.value } : {}) } })
  fetchProducts()
}

function doSearch() {
  page.value = 1
  fetchProducts()
}
</script>

<style scoped>
.product-list-page { background: #f5f5f5; min-height: calc(100vh - 100px); padding: 16px 0; }
.layout-container { max-width: 1200px; margin: 0 auto; padding: 0 12px; display: flex; gap: 16px; }
.category-sidebar { width: 150px; flex-shrink: 0; background: #fff; border-radius: 8px; overflow: hidden; align-self: flex-start; position: sticky; top: 80px; padding: 4px 0; }
.cat-item-all { font-weight: 600; color: #00a854 !important; }
.cat-divider { height: 1px; background: #f0f0f0; margin: 4px 12px; }
.cat-item { padding: 10px 16px; font-size: 13px; cursor: pointer; color: #555; transition: all .15s; }
.cat-item:hover { background: #f0f9f5; color: #00a854; padding-left: 20px; }
.cat-item.active { background: #f0f9f5; color: #00a854; font-weight: 600; border-left: 3px solid #00a854; padding-left: 13px; }
.product-main { flex: 1; }
.toolbar { background: #fff; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; display: flex; align-items: center; }
.result-count { margin-left: 12px; font-size: 13px; color: #888; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.product-card { background: #fff; border-radius: 8px; overflow: hidden; cursor: pointer; transition: box-shadow .2s; }
.product-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.12); transform: translateY(-2px); }
.product-img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.product-info { padding: 10px; }
.product-name { font-size: 13px; color: #333; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; height: 38px; line-height: 1.4; }
.product-tags { margin: 4px 0; min-height: 20px; }
.product-price { margin-top: 6px; }
.points { font-size: 18px; font-weight: 700; color: #f60; }
.unit { font-size: 12px; color: #f60; margin-left: 2px; }
.product-sales { font-size: 12px; color: #bbb; margin-top: 4px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; padding-bottom: 16px; }
</style>
