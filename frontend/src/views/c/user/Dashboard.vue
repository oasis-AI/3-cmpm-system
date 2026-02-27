<template>
  <div class="user-dashboard">
    <!-- 积分卡片 -->
    <div class="points-card">
      <div class="points-left">
        <div class="points-label">我的积分</div>
        <div class="points-value">{{ dashboard.points_balance?.toLocaleString() ?? '—' }}</div>
        <div class="points-sub">积分可用于兑换商品、充值话费</div>
      </div>
      <div class="points-actions">
        <router-link to="/user/points" class="pts-btn">积分明细</router-link>
        <router-link to="/recharge" class="pts-btn pts-btn-outline">去充值</router-link>
      </div>
    </div>

    <!-- 签到卡片 -->
    <div class="checkin-card">
      <div class="checkin-header">
        <span class="checkin-title">每日签到</span>
        <span class="streak-badge" v-if="checkin.streak_days > 0">连签 {{ checkin.streak_days }} 天</span>
      </div>
      <div class="checkin-body">
        <div class="checkin-info">
          <span v-if="checkin.checked_in_today" class="checked-text">✅ 今日已签到，获得 {{ todayPoints }} 积分</span>
          <span v-else class="unchecked-text">签到可得 <b>{{ checkin.next_points }}</b> 积分（连签奖励更多）</span>
        </div>
        <el-button
          type="primary"
          :disabled="checkin.checked_in_today"
          :loading="checkinLoading"
          @click="doCheckin"
          round
        >
          {{ checkin.checked_in_today ? '已签到' : '立即签到' }}
        </el-button>
      </div>
      <!-- 7天进度条 -->
      <div class="streak-dots">
        <div
          v-for="i in 7"
          :key="i"
          class="streak-dot"
          :class="{ active: i <= (checkin.streak_days % 7 || (checkin.streak_days > 0 && checkin.streak_days % 7 === 0 ? 7 : 0)), bonus: i === 7 }"
        >
          <span class="dot-day">第{{ i }}天</span>
          <span class="dot-pts">{{ i === 7 ? '20' : '10' }}</span>
        </div>
      </div>
    </div>

    <!-- 订单状态快捷入口 -->
    <div class="order-status-card">
      <div class="card-title">我的订单</div>
      <div class="order-status-grid">
        <router-link to="/user/orders?tab=pending" class="order-status-item">
          <el-badge :value="dashboard.orders?.pending || ''" :hidden="!dashboard.orders?.pending">
            <el-icon :size="28"><Clock /></el-icon>
          </el-badge>
          <span>待付款</span>
        </router-link>
        <router-link to="/user/orders?tab=paid" class="order-status-item">
          <el-badge :value="dashboard.orders?.paid || ''" :hidden="!dashboard.orders?.paid">
            <el-icon :size="28"><CreditCard /></el-icon>
          </el-badge>
          <span>待发货</span>
        </router-link>
        <router-link to="/user/orders?tab=shipped" class="order-status-item">
          <el-badge :value="dashboard.orders?.shipped || ''" :hidden="!dashboard.orders?.shipped">
            <el-icon :size="28"><Van /></el-icon>
          </el-badge>
          <span>待收货</span>
        </router-link>
        <router-link to="/user/orders?tab=completed" class="order-status-item">
          <el-icon :size="28"><CircleCheck /></el-icon>
          <span>已完成</span>
        </router-link>
        <router-link to="/user/orders" class="order-status-item">
          <el-icon :size="28"><List /></el-icon>
          <span>全部订单</span>
        </router-link>
      </div>
    </div>

    <!-- 快捷功能入口 -->
    <div class="quick-links-card">
      <div class="card-title">常用功能</div>
      <div class="quick-links-grid">
        <router-link to="/user/profile" class="ql-item"><el-icon><User /></el-icon><span>个人信息</span></router-link>
        <router-link to="/user/addresses" class="ql-item"><el-icon><Location /></el-icon><span>收货地址</span></router-link>
        <router-link to="/recharge" class="ql-item"><el-icon><Phone /></el-icon><span>话费充值</span></router-link>
        <router-link to="/activities" class="ql-item"><el-icon><Star /></el-icon><span>限时活动</span></router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, CreditCard, Van, CircleCheck, List, User, Location, Phone, Star } from '@element-plus/icons-vue'
import { userApi } from '@/api/user'

const dashboard = ref<any>({ points_balance: 0, orders: {}, checkin: {} })
const checkin = ref<any>({ checked_in_today: false, streak_days: 0, next_points: 10 })
const checkinLoading = ref(false)
const todayPoints = ref(0)

async function load() {
  try {
    const r: any = await userApi.dashboard()
    dashboard.value = r.data || {}
    checkin.value = r.data?.checkin || {}
  } catch {}
}

async function doCheckin() {
  checkinLoading.value = true
  try {
    const r: any = await userApi.checkin()
    const d = r.data
    ElMessage.success(d.message || `签到成功！获得 ${d.points_earned} 积分`)
    todayPoints.value = d.points_earned
    checkin.value.checked_in_today = true
    checkin.value.streak_days = d.streak_days
    dashboard.value.points_balance = (dashboard.value.points_balance || 0) + d.points_earned
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '签到失败')
  } finally {
    checkinLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.user-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.points-card {
  background: linear-gradient(135deg, #00a854 0%, #00c96e 100%);
  border-radius: 12px;
  padding: 24px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .points-label { font-size: 14px; opacity: 0.85; margin-bottom: 8px; }
  .points-value { font-size: 40px; font-weight: 700; letter-spacing: -1px; }
  .points-sub { font-size: 12px; opacity: 0.7; margin-top: 6px; }

  .points-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .pts-btn {
    display: block;
    padding: 8px 20px;
    border-radius: 20px;
    background: rgba(255,255,255,0.25);
    color: #fff;
    text-decoration: none;
    font-size: 13px;
    text-align: center;
    transition: background 0.2s;
    &:hover { background: rgba(255,255,255,0.4); }
    &.pts-btn-outline {
      background: transparent;
      border: 1px solid rgba(255,255,255,0.6);
    }
  }
}

.checkin-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #f0f0f0;

  .checkin-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    .checkin-title { font-size: 16px; font-weight: 600; }
    .streak-badge {
      background: #ff6600;
      color: #fff;
      font-size: 12px;
      padding: 2px 10px;
      border-radius: 10px;
    }
  }

  .checkin-body {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    .checkin-info { font-size: 14px; color: #555; }
    .checked-text { color: #00a854; }
    .unchecked-text b { color: #ff6600; }
  }

  .streak-dots {
    display: flex;
    gap: 8px;
    .streak-dot {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 8px 4px;
      border-radius: 8px;
      background: #f5f5f5;
      font-size: 11px;
      color: #999;
      .dot-day { margin-bottom: 2px; }
      .dot-pts { font-weight: 600; color: #ccc; }

      &.active {
        background: #e8f9ef;
        color: #00a854;
        .dot-pts { color: #00a854; }
      }
      &.bonus {
        background: #fff7e6;
        .dot-pts { color: #ff6600; }
        &.active { background: #ff6600; color: #fff; .dot-pts { color: #fff; } }
      }
    }
  }
}

.order-status-card, .quick-links-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #f0f0f0;
  .card-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
}

.order-status-grid {
  display: flex;
  justify-content: space-around;
  .order-status-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: #333;
    font-size: 12px;
    .el-icon { color: #00a854; }
    &:hover .el-icon { color: #ff6600; }
  }
}

.quick-links-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  .ql-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 16px 8px;
    border-radius: 8px;
    background: #f9f9f9;
    text-decoration: none;
    color: #333;
    font-size: 12px;
    transition: background 0.2s;
    .el-icon { font-size: 22px; color: #00a854; }
    &:hover { background: #e8f9ef; }
  }
}
</style>
