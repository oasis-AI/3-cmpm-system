<template>
  <div class="search-page">
    <div class="search-container">
      <div class="search-bar">
        <el-input v-model="keyword" placeholder="搜索商品" size="large" clearable @keyup.enter="doSearch(1)" style="max-width:500px">
          <template #append>
            <el-button type="primary" @click="doSearch(1)">搜索</el-button>
          </template>
        </el-input>
      </div>
      <div class="result-info" v-if="searched">共找到 <b>{{ total }}</b> 件「{{ keyword }}」相关商品</div>
      <div v-loading="loading" style="min-height:200px;margin-top:12px">
        <el-empty v-if="searched && !loading && !list.length" description="没有找到相关商品" />
        <div class="product-grid">
          <div v-for="p in list" :key="p.id" class="product-card" @click="$router.push(`/products/${p.id}`)">
            <img :src="p.cover_image || 'https://via.placeholder.com/220'" class="product-img" />
            <div class="product-info">
              <div class="product-name">{{ p.name }}</div>
              <div class="product-pts">{{ p.min_points?.toLocaleString() }} 积分起</div>
            </div>
          </div>
        </div>
      </div>
      <div class="pagination-wrap">
        <el-pagination v-if="total > 0" background layout="prev,pager,next" :total="total" :page-size="pageSize" v-model:current-page="page" @update:current-page="doSearch" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productsApi } from '@/api/products'

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const list = ref<any[]>([])
const loading = ref(false)
const searched = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 20

async function doSearch(p?: number) {
  if (!keyword.value.trim()) return
  if (p) page.value = p
  loading.value = true; searched.value = true
  router.replace({ query: { keyword: keyword.value } })
  try {
    const r: any = await productsApi.list({ page: page.value, page_size: pageSize, keyword: keyword.value })
    list.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}

onMounted(() => {
  keyword.value = String(route.query.keyword || '')
  if (keyword.value) doSearch(1)
})
</script>

<style scoped>
.search-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 24px 0; }
.search-container { max-width: 1100px; margin: 0 auto; padding: 0 12px; }
.search-bar { display: flex; justify-content: center; margin-bottom: 24px; }
.result-info { font-size: 14px; color: #888; margin-bottom: 8px; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.product-card { background: #fff; border-radius: 8px; overflow: hidden; cursor: pointer; transition: box-shadow .2s; }
.product-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.12); }
.product-img { width: 100%; aspect-ratio: 1; object-fit: cover; }
.product-info { padding: 10px; }
.product-name { font-size: 13px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.product-pts { color: #f60; font-weight: 600; font-size: 14px; margin-top: 4px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 20px; }
</style>

