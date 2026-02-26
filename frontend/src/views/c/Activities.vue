<template>
  <div class="activities-page">
    <div class="activities-container">
      <div class="page-title">限时活动</div>
      <div v-loading="loading" style="min-height:200px">
        <el-empty v-if="!loading && !list.length" description="暂无活动" />
        <div class="activity-grid">
          <el-card v-for="a in list" :key="a.id" class="activity-card">
            <img :src="a.banner_image || 'https://via.placeholder.com/360x160'" class="activity-banner" />
            <div class="activity-body">
              <div class="activity-title">{{ a.title }}</div>
              <div class="activity-desc">{{ a.description }}</div>
              <div class="activity-meta">
                <span class="activity-time">{{ a.start_time?.slice(0, 10) }} ~ {{ a.end_time?.slice(0, 10) }}</span>
                <el-tag size="small" :type="statusTag(a.status)">{{ statusLabel(a.status) }}</el-tag>
              </div>
              <el-button type="primary" size="small" style="margin-top:10px" @click="join(a)" :disabled="a.status !== 'active'">
                {{ a.status === 'active' ? '立即参与' : '活动未开始' }}
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { activitiesApi } from '@/api/activities'

const list = ref<any[]>([])
const loading = ref(false)
const statusMap: Record<string, string> = { active: '进行中', pending: '即将开始', ended: '已结束' }
const tagMap: Record<string, string> = { active: 'success', pending: 'warning', ended: 'info' }
const statusLabel = (s: string) => statusMap[s] || s
const statusTag = (s: string) => (tagMap[s] || '') as any

async function load() {
  loading.value = true
  try { const r: any = await activitiesApi.list(); list.value = r.data?.items || r.data || [] }
  finally { loading.value = false }
}
async function join(a: any) {
  await activitiesApi.participate(a.id)
  ElMessage.success('参与成功！')
}
onMounted(load)
</script>

<style scoped>
.activities-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.activities-container { max-width: 1100px; margin: 0 auto; padding: 0 12px; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 16px; }
.activity-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.activity-card { overflow: hidden; }
.activity-banner { width: 100%; height: 150px; object-fit: cover; }
.activity-body { padding: 12px 0 0; }
.activity-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.activity-desc { font-size: 13px; color: #888; margin-bottom: 8px; }
.activity-meta { display: flex; justify-content: space-between; align-items: center; }
.activity-time { font-size: 12px; color: #bbb; }
</style>

