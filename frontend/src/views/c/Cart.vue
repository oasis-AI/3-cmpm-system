<template>
  <div class="cart-page">
    <div class="cart-container">
      <div class="page-title">我的购物车</div>
      <div v-if="loading" v-loading="loading" style="height:200px" />
      <el-empty v-else-if="!items.length" description="购物车空空如也" style="padding:60px 0">
        <el-button type="primary" @click="$router.push('/')">去选商品</el-button>
      </el-empty>
      <template v-else>
        <div class="cart-table">
          <div class="cart-header">
            <el-checkbox v-model="allChecked" @change="toggleAll">全选</el-checkbox>
            <span class="col-product">商品</span>
            <span class="col-price">积分单价</span>
            <span class="col-qty">数量</span>
            <span class="col-sub">小计</span>
            <span class="col-action">操作</span>
          </div>
          <div v-for="item in items" :key="item.id" class="cart-row">
            <el-checkbox v-model="item.checked" @change="syncAll" />
            <div class="col-product product-info">
              <img :src="item.cover_image || 'https://via.placeholder.com/80'" class="product-img" @click="$router.push(`/products/${item.product_id}`)" />
              <div class="product-name">{{ item.product_name }}<br><small>{{ item.sku_name }}</small></div>
            </div>
            <div class="col-price">{{ item.points_price?.toLocaleString() }} 积分</div>
            <div class="col-qty">
              <el-input-number v-model="item.quantity" :min="1" :max="99" size="small" @change="updateQty(item)" />
            </div>
            <div class="col-sub sub-total">{{ (item.points_price * item.quantity).toLocaleString() }} 积分</div>
            <div class="col-action"><el-button link type="danger" @click="removeItem(item.id)">删除</el-button></div>
          </div>
        </div>
        <!-- 底部结算栏 -->
        <div class="cart-footer">
          <div class="left">
            <el-checkbox v-model="allChecked" @change="toggleAll">全选</el-checkbox>
            <el-button link type="danger" @click="clearCart" style="margin-left:16px">清空购物车</el-button>
          </div>
          <div class="right">
            <span>已选 <b>{{ checkedCount }}</b> 件，合计：</span>
            <span class="total-points">{{ totalPoints.toLocaleString() }} <small>积分</small></span>
            <el-button type="primary" size="large" :disabled="!checkedCount" @click="checkout">去结算</el-button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cartApi } from '@/api/cart'
import { useCartStore } from '@/stores/cart'

interface CartItem { id: number; product_id: number; product_name: string; cover_image: string; sku_id: number; sku_name: string; points_price: number; quantity: number; checked: boolean }

const router = useRouter()
const cartStore = useCartStore()
const loading = ref(true)
const items = ref<CartItem[]>([])
const allChecked = ref(false)

const checkedCount = computed(() => items.value.filter(i => i.checked).reduce((s, i) => s + i.quantity, 0))
const totalPoints = computed(() => items.value.filter(i => i.checked).reduce((s, i) => s + i.points_price * i.quantity, 0))

async function load() {
  loading.value = true
  try {
    const r: any = await cartApi.list()
    items.value = (r.data?.items || r.data || []).map((i: any) => ({ ...i, checked: true }))
    cartStore.setCount(items.value.reduce((s, i) => s + i.quantity, 0))
    syncAll()
  } finally { loading.value = false }
}

function toggleAll(val: boolean) { items.value.forEach(i => i.checked = val) }
function syncAll() { allChecked.value = items.value.length > 0 && items.value.every(i => i.checked) }

async function updateQty(item: CartItem) {
  await cartApi.update(item.id, item.quantity)
}
async function removeItem(id: number) {
  await ElMessageBox.confirm('确认删除该商品？', '提示', { type: 'warning' })
  await cartApi.remove(id)
  await load()
}
async function clearCart() {
  await ElMessageBox.confirm('确认清空购物车？', '提示', { type: 'warning' })
  await cartApi.clear()
  await load()
}
function checkout() {
  const checked = items.value.filter(i => i.checked)
  if (!checked.length) { ElMessage.warning('请选择要结算的商品'); return }
  // 传递选中的 cart item ids
  const ids = checked.map(i => i.id).join(',')
  router.push({ path: '/checkout', query: { cart_ids: ids } })
}

onMounted(load)
</script>

<style scoped>
.cart-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 20px 0; }
.cart-container { max-width: 1100px; margin: 0 auto; padding: 0 12px; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 16px; }
.cart-table { background: #fff; border-radius: 8px; overflow: hidden; }
.cart-header, .cart-row { display: flex; align-items: center; padding: 12px 16px; gap: 12px; border-bottom: 1px solid #f0f0f0; font-size: 13px; color: #888; }
.cart-row { color: #222; }
.col-product { flex: 2; }
.col-price, .col-qty, .col-sub, .col-action { flex: 1; text-align: center; }
.product-info { display: flex; align-items: center; gap: 12px; }
.product-img { width: 70px; height: 70px; object-fit: cover; border-radius: 6px; cursor: pointer; }
.product-name { font-size: 14px; line-height: 1.5; }
.sub-total { color: #f60; font-weight: 600; }
.cart-footer { background: #fff; border-radius: 8px; margin-top: 12px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; bottom: 0; }
.right { display: flex; align-items: center; gap: 16px; font-size: 14px; }
.total-points { font-size: 24px; font-weight: 700; color: #f60; }
.total-points small { font-size: 14px; }
</style>

