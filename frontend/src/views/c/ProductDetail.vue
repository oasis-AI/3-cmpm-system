<template>
  <div class="detail-page" v-loading="loading">
    <div class="detail-container" v-if="product">
      <!-- 主图 + 基础信息 -->
      <div class="top-section">
        <div class="img-wrap">
          <img :src="activeImg || product.cover_image || 'https://via.placeholder.com/400'" class="main-img" />
          <div class="thumbnail-list">
            <img
              v-for="(img, i) in product.images"
              :key="i"
              :src="img.url"
              class="thumb"
              :class="{ active: activeImg === img.url }"
              @click="activeImg = img.url"
            />
          </div>
        </div>
        <div class="info-section">
          <div class="product-name">{{ product.name }}</div>
          <div class="brand" v-if="product.brand">品牌：{{ product.brand }}</div>
          <div class="price-row">
            <span class="points">{{ selectedSku?.points_price?.toLocaleString() || product.points_price?.toLocaleString() }}</span>
            <span class="unit">积分兑换</span>
          </div>
          <!-- SKU 选择 -->
          <div class="sku-section" v-if="product.skus?.length">
            <div class="label">规格</div>
            <div class="sku-list">
              <div
                v-for="s in product.skus"
                :key="s.id"
                class="sku-tag"
                :class="{ active: selectedSku?.id === s.id }"
                @click="selectedSku = s"
              >{{ s.sku_name }}</div>
            </div>
          </div>
          <!-- 数量 -->
          <div class="qty-row">
            <span class="label">数量</span>
            <el-input-number v-model="qty" :min="1" :max="99" />
          </div>
          <!-- 积分余额提示 -->
          <div class="balance-hint">我的积分：<b>{{ authStore.userInfo?.points_balance?.toLocaleString() || '—' }}</b></div>
          <!-- 操作按钮 -->
          <div class="action-row">
            <el-button type="warning" size="large" @click="addCart">
              <el-icon><ShoppingCart /></el-icon> 加入购物车
            </el-button>
            <el-button type="primary" size="large" @click="buyNow">立即兑换</el-button>
          </div>
        </div>
      </div>

      <!-- 商品详情 -->
      <div class="description-section" v-if="product.description">
        <div class="section-title">商品详情</div>
        <div class="description-content">{{ product.description }}</div>
      </div>

      <!-- 商品评价 -->
      <div class="description-section" style="margin-top:16px">
        <div class="section-title">
          用户评价
          <span class="avg-rating" v-if="reviewData.avg_rating">
            <el-rate :model-value="reviewData.avg_rating" disabled allow-half show-score />
            （{{ reviewData.total }} 条）
          </span>
          <span v-else style="font-size:13px;color:#bbb;font-weight:400;margin-left:12px">暂无评价</span>
        </div>
        <div v-if="reviewData.items.length">
          <div v-for="r in reviewData.items" :key="r.id" class="review-item">
            <div class="review-header">
              <el-avatar :size="32" style="flex-shrink:0">{{ r.nickname.charAt(0) }}</el-avatar>
              <div>
                <div class="review-user">{{ r.nickname }}</div>
                <el-rate :model-value="r.rating" disabled size="small" />
              </div>
              <span class="review-time">{{ r.created_at?.slice(0, 10) }}</span>
            </div>
            <div class="review-content">{{ r.content || '该用户没有填写评价' }}</div>
          </div>
          <div class="pagination-wrap">
            <el-pagination
              background
              layout="prev,pager,next"
              :total="reviewData.total"
              :page-size="10"
              v-model:current-page="reviewPage"
              @update:current-page="loadReviews"
            />
          </div>
        </div>
        <el-empty v-else description="暂无评价，快来抢占沙发！" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ShoppingCart } from '@element-plus/icons-vue'
import { productsApi } from '@/api/products'
import { cartApi } from '@/api/cart'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const product = ref<any>(null)
const selectedSku = ref<any>(null)
const activeImg = ref('')
const qty = ref(1)
const reviewPage = ref(1)
const reviewData = ref<{ items: any[]; total: number; avg_rating: number | null }>({
  items: [], total: 0, avg_rating: null,
})

onMounted(async () => {
  try {
    const r: any = await productsApi.detail(Number(route.params.id))
    product.value = r.data
    if (product.value.skus?.length) {
      selectedSku.value = product.value.skus[0]
    } else {
      selectedSku.value = {
        id: product.value.id,
        sku_name: '默认',
        points_price: product.value.points_price ?? product.value.min_points ?? 0,
        stock: product.value.stock ?? 99,
      }
    }
    if (product.value.images?.length) activeImg.value = product.value.images[0].url
    await loadReviews()
  } finally {
    loading.value = false
  }
})

async function loadReviews() {
  try {
    const r: any = await productsApi.reviews(Number(route.params.id), { page: reviewPage.value, page_size: 10 })
    reviewData.value = r.data ?? { items: [], total: 0, avg_rating: null }
  } catch {}
}

async function addCart() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  if (!selectedSku.value) { ElMessage.warning('请选择规格'); return }
  await cartApi.add({ sku_id: selectedSku.value.id, quantity: qty.value })
  ElMessage.success('已加入购物车')
}

async function buyNow() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  if (!selectedSku.value) { ElMessage.warning('请选择规格'); return }
  router.push({ path: '/checkout', query: { product_id: product.value.id, sku_id: selectedSku.value.id, qty: qty.value } })
}
</script>

<style scoped>
.detail-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.detail-container { max-width: 1100px; margin: 0 auto; padding: 0 12px; }
.top-section { display: flex; gap: 32px; background: #fff; border-radius: 8px; padding: 24px; }
.img-wrap { flex-shrink: 0; }
.main-img { width: 380px; height: 380px; object-fit: cover; border-radius: 8px; display: block; }
.thumbnail-list { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.thumb { width: 60px; height: 60px; object-fit: cover; border: 2px solid transparent; border-radius: 4px; cursor: pointer; }
.thumb.active { border-color: #00a854; }
.info-section { flex: 1; }
.product-name { font-size: 20px; font-weight: 600; color: #222; margin-bottom: 8px; }
.brand { font-size: 13px; color: #888; margin-bottom: 12px; }
.price-row { background: #fff9f0; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; }
.points { font-size: 32px; font-weight: 700; color: #f60; }
.unit { font-size: 14px; color: #f60; margin-left: 6px; }
.sku-section { margin-bottom: 16px; }
.label { font-size: 14px; color: #666; margin-bottom: 8px; }
.sku-list { display: flex; flex-wrap: wrap; gap: 8px; }
.sku-tag { padding: 6px 14px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; font-size: 13px; }
.sku-tag.active { border-color: #00a854; color: #00a854; background: #f0f9f5; }
.qty-row { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; font-size: 14px; }
.balance-hint { font-size: 13px; color: #888; margin-bottom: 20px; }
.action-row { display: flex; gap: 12px; }
.description-section { background: #fff; border-radius: 8px; padding: 24px; margin-top: 16px; }
.section-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; border-left: 4px solid #00a854; padding-left: 12px; }
.description-content { font-size: 14px; color: #555; line-height: 1.8; white-space: pre-wrap; }
.avg-rating { display: inline-flex; align-items: center; gap: 4px; margin-left: 12px; font-size: 13px; font-weight: 400; }
.review-item { padding: 16px 0; border-bottom: 1px solid #f5f5f5; }
.review-item:last-child { border: none; }
.review-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.review-user { font-size: 13px; font-weight: 600; }
.review-time { margin-left: auto; font-size: 12px; color: #bbb; }
.review-content { font-size: 14px; color: #555; padding-left: 42px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 12px; }
</style>

