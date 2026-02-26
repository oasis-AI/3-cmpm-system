<template>
  <div class="checkout-page">
    <div class="checkout-container">
      <div class="page-title">确认订单</div>
      <!-- 收货地址 -->
      <div class="section">
        <div class="section-title">收货地址</div>
        <div v-if="!addresses.length" class="no-addr">
          <span>暂无地址，</span>
          <el-button link type="primary" @click="$router.push('/user/addresses')">去添加</el-button>
        </div>
        <div v-else class="addr-list">
          <div
            v-for="a in addresses"
            :key="a.id"
            class="addr-card"
            :class="{ selected: selectedAddr?.id === a.id }"
            @click="selectedAddr = a"
          >
            <div class="addr-name">{{ a.receiver_name }} {{ a.receiver_phone }}</div>
            <div class="addr-text">{{ a.province }}{{ a.city }}{{ a.district }}{{ a.detail }}</div>
            <el-tag v-if="a.is_default" size="small" type="success" style="margin-top:4px">默认</el-tag>
          </div>
        </div>
      </div>

      <!-- 商品列表 -->
      <div class="section">
        <div class="section-title">兑换商品</div>
        <div v-for="item in orderItems" :key="item.sku_id" class="order-item">
          <img :src="item.cover_image || 'https://via.placeholder.com/60'" class="item-img" />
          <div class="item-info">
            <div class="item-name">{{ item.name }}<small v-if="item.sku_name"> — {{ item.sku_name }}</small></div>
            <div class="item-pts">{{ item.points_price?.toLocaleString() }} 积分 × {{ item.qty }}</div>
          </div>
          <div class="item-sub">{{ (item.points_price * item.qty).toLocaleString() }} 积分</div>
        </div>
      </div>

      <!-- 结算栏 -->
      <div class="summary-bar">
        <div class="balance-row">我的积分余额：<b>{{ balance?.toLocaleString() }}</b></div>
        <div class="total-row">需消耗积分：<span class="total-pts">{{ totalPoints.toLocaleString() }}</span></div>
        <div v-if="balance < totalPoints" class="warn">积分不足</div>
        <el-button type="primary" size="large" :disabled="!selectedAddr || balance < totalPoints || submitting" @click="submit">
          {{ submitting ? '提交中...' : '提交订单' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'
import { ordersApi } from '@/api/orders'
import { pointsApi } from '@/api/points'
import { productsApi } from '@/api/products'
import { cartApi } from '@/api/cart'

const route = useRoute()
const router = useRouter()
const addresses = ref<any[]>([])
const selectedAddr = ref<any>(null)
const balance = ref(0)
const orderItems = ref<any[]>([])
const submitting = ref(false)
const totalPoints = computed(() => orderItems.value.reduce((s, i) => s + i.points_price * i.qty, 0))

onMounted(async () => {
  const [addrR, balR]: any[] = await Promise.all([userApi.addresses(), pointsApi.balance()])
  addresses.value = addrR.data || []
  balance.value = balR.data?.balance ?? 0
  selectedAddr.value = addresses.value.find((a: any) => a.is_default) ?? (addresses.value[0] || null)

  // 根据 query 构建 orderItems
  const { sku_id, qty, cart_ids, product_id } = route.query
  if (sku_id && product_id) {
    try {
      const r: any = await productsApi.detail(Number(product_id))
      const prod = r.data
      const sku = (prod.skus || []).find((s: any) => String(s.id) === String(sku_id))
      orderItems.value = [{
        sku_id: Number(sku_id),
        name: prod.name || '商品',
        sku_name: sku?.sku_name || '',
        points_price: sku?.points_price ?? prod.points_price ?? prod.min_points ?? 0,
        cover_image: prod.cover_image,
        qty: Number(qty) || 1
      }]
    } catch {
      ElMessage.error('商品信息加载失败')
    }
  } else if (cart_ids) {
    const r: any = await cartApi.list()
    const ids = String(cart_ids).split(',').map(Number)
    orderItems.value = (r.data?.items || r.data || [])
      .filter((i: any) => ids.includes(i.id))
      .map((i: any) => ({ sku_id: i.sku_id, name: i.product_name, sku_name: i.sku_name, points_price: i.points_price, cover_image: i.cover_image, qty: i.quantity }))
  }
})

async function submit() {
  if (!selectedAddr.value) { ElMessage.warning('请选择收货地址'); return }
  if (!orderItems.value.length) { ElMessage.warning('没有可下单的商品'); return }
  submitting.value = true
  try {
    for (const item of orderItems.value) {
      await ordersApi.create({ sku_id: item.sku_id, quantity: item.qty, address_id: selectedAddr.value.id })
    }
    ElMessage.success('下单成功！')
    router.push('/user/orders')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.checkout-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.checkout-container { max-width: 900px; margin: 0 auto; padding: 0 12px; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 16px; }
.section { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 12px; border-left: 4px solid #00a854; padding-left: 10px; }
.addr-list { display: flex; flex-wrap: wrap; gap: 12px; }
.addr-card { border: 2px solid #e8e8e8; border-radius: 8px; padding: 12px 16px; cursor: pointer; min-width: 200px; transition: border-color .2s; }
.addr-card.selected { border-color: #00a854; background: #f0f9f5; }
.addr-name { font-weight: 600; margin-bottom: 4px; }
.addr-text { font-size: 13px; color: #666; }
.no-addr { font-size: 14px; color: #888; }
.order-item { display: flex; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.order-item:last-child { border: none; }
.item-img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
.item-info { flex: 1; }
.item-name { font-size: 14px; }
.item-pts { font-size: 13px; color: #888; margin-top: 4px; }
.item-sub { font-weight: 600; color: #f60; white-space: nowrap; }
.summary-bar { background: #fff; border-radius: 8px; padding: 20px; display: flex; justify-content: flex-end; align-items: center; gap: 20px; font-size: 14px; }
.balance-row { color: #888; }
.total-row { font-weight: 600; }
.total-pts { font-size: 22px; color: #f60; }
.warn { color: #f56c6c; }
</style>

