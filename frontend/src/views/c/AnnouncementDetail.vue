<template>
  <div class="announce-detail-page">
    <div class="announce-detail-container" v-loading="loading">
      <el-button link @click="$router.push('/announcements')" style="margin-bottom:12px">← 返回公告列表</el-button>
      <el-card v-if="item">
        <div class="detail-title">{{ item.title }}</div>
        <div class="detail-meta">
          <el-tag size="small" type="info">{{ item.type || '公告' }}</el-tag>
          <span class="detail-date">发布时间：{{ item.created_at?.slice(0, 16) }}</span>
        </div>
        <el-divider />
        <div class="detail-content">{{ item.content }}</div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/api/request'

const route = useRoute()
const loading = ref(true)
const item = ref<any>(null)

onMounted(async () => {
  try {
    const r: any = await request.get(`/announcements/${route.params.id}`)
    item.value = r.data
  } finally { loading.value = false }
})
</script>

<style scoped>
.announce-detail-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.announce-detail-container { max-width: 800px; margin: 0 auto; padding: 0 12px; }
.detail-title { font-size: 22px; font-weight: 700; color: #111; margin-bottom: 12px; }
.detail-meta { display: flex; align-items: center; gap: 12px; }
.detail-date { font-size: 13px; color: #bbb; }
.detail-content { font-size: 15px; color: #444; line-height: 2; white-space: pre-wrap; }
</style>

