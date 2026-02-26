<template>
  <div class="announce-page">
    <div class="announce-container">
      <div class="page-title">公告中心</div>
      <div v-loading="loading" style="min-height:200px">
        <el-empty v-if="!loading && !list.length" description="暂无公告" />
        <div v-for="item in list" :key="item.id" class="announce-item" @click="$router.push(`/announcements/${item.id}`)">
          <div class="item-title">{{ item.title }}</div>
          <div class="item-meta">
            <el-tag size="small" type="info">{{ typeLabel(item.type) }}</el-tag>
            <span class="item-date">{{ item.created_at?.slice(0, 10) }}</span>
          </div>
          <div class="item-excerpt">{{ item.content?.slice(0, 80) }}{{ item.content?.length > 80 ? '...' : '' }}</div>
        </div>
      </div>
      <div class="pagination-wrap">
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="10" v-model:current-page="page" @update:current-page="load" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { activitiesApi } from '@/api/activities'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const typeMap: Record<string, string> = { activity: '活动', system: '系统', promotion: '促销' }
const typeLabel = (t: string) => typeMap[t] || t

async function load() {
  loading.value = true
  try {
    const r: any = await activitiesApi.announcements({ page: page.value, page_size: 10 })
    list.value = r.data?.items || r.data || []
    total.value = r.data?.total || 0
  } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.announce-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.announce-container { max-width: 800px; margin: 0 auto; padding: 0 12px; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 16px; }
.announce-item { background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 10px; cursor: pointer; transition: box-shadow .2s; }
.announce-item:hover { box-shadow: 0 2px 12px rgba(0,0,0,.1); }
.item-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #222; }
.item-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.item-date { font-size: 13px; color: #bbb; }
.item-excerpt { font-size: 13px; color: #888; line-height: 1.6; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>

