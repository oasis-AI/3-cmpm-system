<template>
  <div class="home">
    <!-- Banner 轮播 -->
    <section class="banner-section">
      <el-carousel height="360px" :interval="4000">
        <el-carousel-item v-for="(item, i) in banners" :key="i">
          <div class="banner-slide" :style="{ background: item.bg }">
            <div class="banner-content">
              <h2>{{ item.title }}</h2>
              <p>{{ item.sub }}</p>
              <el-button type="primary" size="large" @click="router.push(item.link)">
                {{ item.btn }}
              </el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <div class="home-body">
      <!-- 快捷入口 -->
      <section class="quick-entry">
        <div class="entry-grid">
          <router-link v-for="e in entries" :key="e.label" :to="e.link" class="entry-item">
            <el-icon :size="32" :color="e.color"><component :is="e.icon" /></el-icon>
            <span>{{ e.label }}</span>
          </router-link>
        </div>
      </section>

      <!-- 公告 -->
      <el-alert
        v-if="announcement"
        :title="announcement"
        type="info"
        show-icon
        :closable="false"
        class="announce-bar"
      />

      <!-- 限时活动 -->
      <section class="home-section">
        <div class="section-header">
          <h3>限时活动</h3>
          <router-link to="/activities">查看全部 &rsaquo;</router-link>
        </div>
        <el-skeleton :rows="2" animated :loading="loading.activities">
          <template #default>
            <div class="activity-cards">
              <el-card
                v-for="act in activities"
                :key="act.id"
                class="activity-card"
                @click="router.push('/activities')"
              >
                <div class="act-tag">
                  <el-tag :type="act.type === 'discount' ? 'danger' : 'warning'" size="small">
                    {{ act.type === 'discount' ? '积分折扣' : '积分兑换' }}
                  </el-tag>
                </div>
                <h4>{{ act.name }}</h4>
                <p class="act-time">{{ act.start_date }} ~ {{ act.end_date }}</p>
              </el-card>
            </div>
          </template>
        </el-skeleton>
      </section>

      <!-- 热门商品 -->
      <section class="home-section">
        <div class="section-header">
          <h3>热门兑换</h3>
          <router-link to="/products">查看全部 &rsaquo;</router-link>
        </div>
        <el-skeleton :rows="3" animated :loading="loading.products">
          <template #default>
            <div class="product-grid">
              <div
                v-for="p in products"
                :key="p.id"
                class="product-card product-card-hover"
                @click="router.push({ name: 'ProductDetail', params: { id: p.id } })"
              >
                <div class="card-img">
                  <img :src="p.cover_image || defaultImg" :alt="p.name" />
                </div>
                <div class="card-body">
                  <p class="card-name">{{ p.name }}</p>
                  <p class="card-points">
                    <span class="points-text">{{ p.points_price }}</span>
                    <span class="points-unit">积分</span>
                  </p>
                </div>
              </div>
            </div>
          </template>
        </el-skeleton>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Phone, Cellphone, Present, Promotion, Star,
} from '@element-plus/icons-vue'
import { productsApi } from '@/api/products'
import { activitiesApi } from '@/api/activities'

const router = useRouter()
const defaultImg = 'https://picsum.photos/300/300?grayscale'

const banners = [
  { title: '积分兑好礼', sub: '海量商品等你来换', btn: '立即兑换', link: '/products', bg: 'linear-gradient(135deg, #00a854 0%, #00c878 100%)' },
  { title: '话费秒充，积分抵扣', sub: '100积分抵1元，最高抵扣50%', btn: '快速充值', link: '/recharge', bg: 'linear-gradient(135deg, #1890ff 0%, #36cfc9 100%)' },
  { title: '限时活动 积分翻倍', sub: '消费即积分，积分更值钱', btn: '查看活动', link: '/activities', bg: 'linear-gradient(135deg, #ff6600 0%, #ffad33 100%)' },
]

const entries = [
  { label: '话费充值', link: '/recharge', icon: Phone, color: '#00a854' },
  { label: '流量套餐', link: '/recharge?type=data', icon: Cellphone, color: '#1890ff' },
  { label: '实物兑换', link: '/products', icon: Present, color: '#ff6600' },
  { label: '限时活动', link: '/activities', icon: Promotion, color: '#f5222d' },
  { label: '积分商城', link: '/products', icon: Star, color: '#faad14' },
]

const announcement = ref('')
const activities = ref<any[]>([])
const products = ref<any[]>([])
const loading = ref({ activities: true, products: true })

onMounted(async () => {
  try {
    const [annRes, actRes, prodRes] = await Promise.allSettled([
      activitiesApi.announcements({ page: 1, page_size: 1 }),
      activitiesApi.list({ page: 1, page_size: 4 }),
      productsApi.list({ page: 1, page_size: 8 }),
    ])

    if (annRes.status === 'fulfilled' && (annRes.value as any).data?.items?.[0]) {
      announcement.value = (annRes.value as any).data.items[0].title
    }
    if (actRes.status === 'fulfilled') {
      activities.value = (actRes.value as any).data?.items || []
    }
    if (prodRes.status === 'fulfilled') {
      products.value = (prodRes.value as any).data?.items || []
    }
  } finally {
    loading.value.activities = false
    loading.value.products = false
  }
})
</script>

<style scoped lang="scss">
.home { background: #f5f5f5; }

.banner-section .banner-slide {
  height: 360px;
  display: flex;
  align-items: center;
  padding: 0 120px;
  color: #fff;

  .banner-content {
    h2 { font-size: 36px; font-weight: 700; margin-bottom: 12px; }
    p { font-size: 18px; opacity: 0.9; margin-bottom: 24px; }
  }
}

.home-body {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 16px;
}

.quick-entry {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}
.entry-grid {
  display: flex;
  gap: 0;
  justify-content: space-around;
}
.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #333;
  font-size: 13px;
  padding: 12px 20px;
  border-radius: 8px;
  transition: background 0.2s;
  &:hover { background: #f0f9eb; }
}

.announce-bar { margin-bottom: 16px; }

.home-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  h3 { font-size: 18px; font-weight: 600; margin: 0; }
  a { color: #999; text-decoration: none; font-size: 13px; &:hover { color: $primary-color; } }
}

.activity-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.activity-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
  h4 { font-size: 14px; margin: 8px 0 4px; }
  .act-time { font-size: 12px; color: #999; }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.product-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  cursor: pointer;

  .card-img {
    aspect-ratio: 1;
    overflow: hidden;
    img { width: 100%; height: 100%; object-fit: cover; }
  }
  .card-body { padding: 10px 12px; }
  .card-name {
    font-size: 13px;
    color: #333;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .card-points {
    .points-text { font-size: 18px; font-weight: 700; }
    .points-unit { font-size: 12px; color: #999; margin-left: 2px; }
  }
}
</style>
