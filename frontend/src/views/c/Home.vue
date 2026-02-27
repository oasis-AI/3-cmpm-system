<template>
  <div class="home">
    <div class="home-layout">
      <!-- 主内容 -->
      <main class="home-main">
        <!-- Banner 轮播 -->
        <el-carousel height="300px" :interval="4000">
          <el-carousel-item v-for="(item, i) in banners" :key="i">
            <div
              class="banner-slide"
              :style="{ backgroundImage: `${item.overlay}, url(${item.img})`, backgroundSize: 'cover', backgroundPosition: 'center' }"
            >
              <div class="banner-content">
                <h2>{{ item.title }}</h2>
                <p>{{ item.sub }}</p>
                <el-button type="primary" size="default" @click="router.push(item.link)">
                  {{ item.btn }}
                </el-button>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>

        <!-- 快捷入口 -->
        <div class="quick-entry">
          <router-link v-for="e in entries" :key="e.label" :to="e.link" class="entry-item">
            <div class="entry-icon" :style="{ background: e.bg }">
              <el-icon :size="22" :color="e.color"><component :is="e.icon" /></el-icon>
            </div>
            <span>{{ e.label }}</span>
          </router-link>
        </div>

        <!-- 公告 -->
        <el-alert
          v-if="announcement"
          :title="'📢 ' + announcement"
          type="info"
          show-icon
          :closable="false"
          class="announce-bar"
        />

        <!-- 限时活动 -->
        <section class="home-section" v-if="activities.length">
          <div class="section-header">
            <span class="section-title"><span class="sec-bar"></span>限时活动</span>
            <router-link to="/activities" class="sec-more">查看全部 ›</router-link>
          </div>
          <div class="activity-cards">
            <div
              v-for="(act, i) in activities"
              :key="act.id"
              class="activity-card"
              :style="{ background: actColors[i % actColors.length] }"
              @click="router.push('/activities')"
            >
              <el-tag :type="act.type === 'discount' ? 'danger' : 'warning'" size="small" effect="dark">
                {{ act.type === 'discount' ? '积分折扣' : '积分兑换' }}
              </el-tag>
              <h4>{{ act.name }}</h4>
              <p>{{ act.start_date?.slice(0,10) }} ~ {{ act.end_date?.slice(0,10) }}</p>
            </div>
          </div>
        </section>

        <!-- 热门商品 -->
        <section class="home-section">
          <div class="section-header">
            <span class="section-title"><span class="sec-bar"></span>热门兑换</span>
            <router-link to="/products" class="sec-more">查看全部 ›</router-link>
          </div>
          <el-skeleton :rows="3" animated :loading="loading.products">
            <template #default>
              <div class="product-grid">
                <div
                  v-for="p in products"
                  :key="p.id"
                  class="product-card"
                  @click="router.push({ name: 'ProductDetail', params: { id: p.id } })"
                >
                  <div class="card-img">
                    <img :src="p.cover_image || defaultImg" :alt="p.name" />
                    <div class="card-badge" v-if="p.status === 'on_sale'">热卖</div>
                  </div>
                  <div class="card-body">
                    <p class="card-name">{{ p.name }}</p>
                    <p class="card-brand" v-if="p.brand">{{ p.brand }}</p>
                    <p class="card-points">
                      <span class="points-num">{{ (p.points_price ?? p.min_points)?.toLocaleString() }}</span>
                      <span class="points-unit">积分</span>
                    </p>
                  </div>
                </div>
              </div>
            </template>
          </el-skeleton>
        </section>
      </main>

      <!-- 右：用户卡片 + 快速充值 -->
      <aside class="home-sidebar">
        <!-- 用户/登录卡片 -->
        <div class="user-widget">
          <template v-if="authStore.isLoggedIn">
            <div class="widget-user-info">
              <el-avatar :size="48" :src="authStore.userInfo?.avatar" class="widget-avatar" />
              <div>
                <div class="widget-name">{{ authStore.userInfo?.nickname }}</div>
                <div class="widget-pts">积分余额：<b>{{ authStore.userInfo?.points_balance?.toLocaleString() ?? '—' }}</b></div>
              </div>
            </div>
            <div class="widget-btns">
              <router-link to="/user" class="w-btn w-btn-primary">个人中心</router-link>
              <router-link to="/user/orders" class="w-btn w-btn-outline">我的订单</router-link>
            </div>
          </template>
          <template v-else>
            <div class="widget-guest">
              <div class="widget-hello">欢迎访问</div>
              <div class="widget-sub">登录后享受更多积分权益</div>
              <div class="widget-btns" style="margin-top:12px">
                <router-link to="/login" class="w-btn w-btn-primary">立即登录</router-link>
                <router-link to="/register" class="w-btn w-btn-outline">免费注册</router-link>
              </div>
            </div>
          </template>
        </div>

        <!-- 公告  -->
        <div class="sidebar-announce" v-if="announcement">
          <div class="sidebar-title">🔔 商城公告</div>
          <p class="announce-text">{{ announcement }}</p>
          <router-link to="/announcements" class="announce-more">更多公告 ›</router-link>
        </div>

        <!-- 快速充值小部件 -->
        <div class="recharge-widget">
          <div class="sidebar-title">⚡ 快速充值</div>
          <div class="rw-tabs">
            <span :class="['rw-tab', rwTab==='phone' && 'active']" @click="rwTab='phone'">话费充值</span>
            <span :class="['rw-tab', rwTab==='data' && 'active']" @click="rwTab='data'">流量充值</span>
          </div>
          <div class="rw-amounts">
            <span
              v-for="a in (rwTab==='phone' ? [10,30,50,100] : [5,20,35,150])"
              :key="a"
              :class="['rw-amt', rwAmount===a && 'selected']"
              @click="rwAmount=a"
            >{{ a }}元</span>
          </div>
          <router-link
            :to="`/recharge?type=${rwTab}&amount=${rwAmount}`"
            class="rw-btn"
          >立即充值（{{ rwAmount * 100 }} 积分）</router-link>
        </div>
      </aside>
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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const defaultImg = 'https://picsum.photos/300/300?grayscale'

const rwTab = ref<'phone' | 'data'>('phone')
const rwAmount = ref(30)

const banners = [
  {
    title: '积分兑好礼',
    sub: '海量商品等你来换',
    btn: '立即兑换',
    link: '/products',
    img: 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1400&q=80',
    overlay: 'linear-gradient(135deg, rgba(0,168,84,0.75) 0%, rgba(0,200,120,0.55) 100%)',
  },
  {
    title: '话费秒充，积分抵扣',
    sub: '100积分抵1元，最高抵扣50%',
    btn: '快速充值',
    link: '/recharge',
    img: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=1400&q=80',
    overlay: 'linear-gradient(135deg, rgba(24,144,255,0.75) 0%, rgba(54,207,201,0.55) 100%)',
  },
  {
    title: '限时活动 积分翻倍',
    sub: '消费即积分，积分更值钱',
    btn: '查看活动',
    link: '/activities',
    img: 'https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=1400&q=80',
    overlay: 'linear-gradient(135deg, rgba(255,102,0,0.75) 0%, rgba(255,173,51,0.55) 100%)',
  },
]

const entries = [
  { label: '话费充值', link: '/recharge', icon: Phone, color: '#00a854', bg: '#e8f5e9' },
  { label: '流量套餐', link: '/recharge?type=data', icon: Cellphone, color: '#1890ff', bg: '#e3f2fd' },
  { label: '实物兑换', link: '/products', icon: Present, color: '#ff6600', bg: '#fff3e0' },
  { label: '限时活动', link: '/activities', icon: Promotion, color: '#f5222d', bg: '#fce4ec' },
  { label: '积分商城', link: '/products', icon: Star, color: '#faad14', bg: '#fff8e1' },
]

const actColors = [
  'linear-gradient(135deg,#e8f5e9,#c8e6c9)',
  'linear-gradient(135deg,#e3f2fd,#bbdefb)',
  'linear-gradient(135deg,#fff3e0,#ffe0b2)',
  'linear-gradient(135deg,#fce4ec,#f8bbd0)',
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
$primary: #00a854;

/* ── 三栏布局 ── */
.home {
  background: #f5f5f5;
  min-height: calc(100vh - 120px);
}

.home-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 12px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

/* ── 主内容 ── */
.home-main {
  flex: 1;
  min-width: 0;
}

/* Banner */
:deep(.el-carousel__item) {
  border-radius: 8px;
  overflow: hidden;
}
.banner-slide {
  height: 300px;
  display: flex;
  align-items: center;
  padding: 0 48px;
  color: #fff;

  .banner-content {
    h2 { font-size: 28px; font-weight: 700; margin-bottom: 10px; text-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    p  { font-size: 15px; opacity: 0.92; margin-bottom: 20px; }
  }
}

/* 快捷入口 */
.quick-entry {
  display: flex;
  justify-content: space-around;
  background: #fff;
  border-radius: 8px;
  padding: 16px 8px;
  margin: 12px 0;
}
.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #333;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  transition: background 0.2s;
  &:hover { background: #f0f9eb; }

  .entry-icon {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* 公告 */
.announce-bar { margin: 0 0 10px; border-radius: 6px; }

/* 通用 section */
.home-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;

  .section-title {
    font-size: 15px;
    font-weight: 600;
    color: #222;
    display: flex;
    align-items: center;
    gap: 8px;

    .sec-bar {
      display: inline-block;
      width: 4px;
      height: 16px;
      background: $primary;
      border-radius: 2px;
    }
  }

  .sec-more {
    color: #999;
    text-decoration: none;
    font-size: 12px;
    &:hover { color: $primary; }
  }
}

/* 活动卡片 */
.activity-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.activity-card {
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  &:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
  h4 { font-size: 13px; margin: 8px 0 4px; color: #333; }
  p  { font-size: 11px; color: #888; }
}

/* 商品网格 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.product-card {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  &:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }

  .card-img {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
    &:hover img { transform: scale(1.05); }

    .card-badge {
      position: absolute;
      top: 8px; right: 8px;
      background: #f5222d;
      color: #fff;
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 10px;
    }
  }

  .card-body { padding: 10px; }

  .card-name {
    font-size: 13px;
    color: #333;
    margin-bottom: 2px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
  }

  .card-brand {
    font-size: 11px;
    color: #aaa;
    margin-bottom: 6px;
  }

  .card-points {
    .points-num { font-size: 17px; font-weight: 700; color: $primary; }
    .points-unit { font-size: 11px; color: #999; margin-left: 2px; }
  }
}

/* ── 右侧边栏 ── */
.home-sidebar {
  width: 210px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 用户 widget */
.user-widget {
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .widget-user-info {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 12px;
  }
  .widget-name { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 4px; }
  .widget-pts  { font-size: 12px; color: #888; b { color: $primary; } }

  .widget-guest {
    text-align: center;
    .widget-hello { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
    .widget-sub   { font-size: 12px; color: #999; }
  }
}

.widget-btns {
  display: flex;
  gap: 8px;

  .w-btn {
    flex: 1;
    display: inline-block;
    text-align: center;
    text-decoration: none;
    padding: 7px 0;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    transition: opacity 0.2s;
    &:hover { opacity: 0.85; }

    &.w-btn-primary { background: $primary; color: #fff; }
    &.w-btn-outline { border: 1px solid $primary; color: $primary; }
  }
}

/* 侧边公告 */
.sidebar-announce {
  background: #fff;
  border-radius: 8px;
  padding: 14px;

  .announce-text { font-size: 12px; color: #555; margin: 8px 0; line-height: 1.6; }
  .announce-more { font-size: 12px; color: $primary; text-decoration: none; &:hover { text-decoration: underline; } }
}

/* 快速充值 widget */
.recharge-widget {
  background: #fff;
  border-radius: 8px;
  padding: 14px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #222;
  margin-bottom: 10px;
}

.rw-tabs {
  display: flex;
  gap: 0;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 10px;
}
.rw-tab {
  flex: 1;
  text-align: center;
  padding: 6px 0;
  font-size: 12px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
  &.active { background: $primary; color: #fff; font-weight: 600; }
}

.rw-amounts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-bottom: 10px;
}
.rw-amt {
  text-align: center;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 6px 0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.18s;
  &:hover { border-color: $primary; color: $primary; }
  &.selected { background: $primary; color: #fff; border-color: $primary; font-weight: 600; }
}

.rw-btn {
  display: block;
  width: 100%;
  text-align: center;
  background: $primary;
  color: #fff;
  text-decoration: none;
  padding: 9px 0;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  transition: opacity 0.2s;
  &:hover { opacity: 0.88; }
}
</style>
