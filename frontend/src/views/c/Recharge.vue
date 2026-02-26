<template>
  <div class="recharge-page">
    <div class="recharge-container">
      <div class="page-title">话费/流量充值</div>
      <div class="balance-tip">当前积分：<b>{{ balance?.toLocaleString() }}</b></div>
      <el-tabs v-model="tab">
        <el-tab-pane label="话费充值" name="phone" />
        <el-tab-pane label="流量充值" name="data" />
      </el-tabs>
      <el-card class="form-card">
        <el-form :model="form" label-width="100px" style="max-width:420px">
          <el-form-item label="手机号">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item :label="tab === 'phone' ? '充值金额' : '流量套餐'">
            <div class="amount-list">
              <div
                v-for="opt in (tab === 'phone' ? phoneOpts : dataOpts)"
                :key="opt.value"
                class="amount-tag"
                :class="{ active: form.amount === opt.value }"
                @click="form.amount = opt.value"
              >
                <div class="opt-label">{{ opt.label }}</div>
                <div class="opt-pts">{{ opt.points.toLocaleString() }} 积分</div>
              </div>
            </div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" @click="submit" :loading="submitting" style="width:100%">
              立即兑换
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { pointsApi } from '@/api/points'

const tab = ref('phone')
const balance = ref(0)
const submitting = ref(false)
const form = ref({ phone: '', amount: 10 })

const phoneOpts = [
  { label: '10元话费', value: 10, points: 1000 },
  { label: '30元话费', value: 30, points: 2900 },
  { label: '50元话费', value: 50, points: 4800 },
  { label: '100元话费', value: 100, points: 9500 },
]
const dataOpts = [
  { label: '100MB流量', value: 100, points: 500 },
  { label: '500MB流量', value: 500, points: 2000 },
  { label: '1GB流量', value: 1000, points: 3500 },
  { label: '5GB流量', value: 5000, points: 15000 },
]

onMounted(async () => {
  const r: any = await pointsApi.balance()
  balance.value = r.data?.balance ?? 0
})

async function submit() {
  if (!form.value.phone) { ElMessage.warning('请输入手机号'); return }
  submitting.value = true
  try {
    await pointsApi.quickRecharge({ phone: form.value.phone, type: tab.value as 'phone' | 'data', amount: form.value.amount })
    ElMessage.success('充值成功！')
    const r: any = await pointsApi.balance()
    balance.value = r.data?.balance ?? 0
  } finally { submitting.value = false }
}
</script>

<style scoped>
.recharge-page { background: #f5f5f5; min-height: calc(100vh - 60px); padding: 24px 0; }
.recharge-container { max-width: 700px; margin: 0 auto; padding: 0 12px; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 6px; }
.balance-tip { font-size: 14px; color: #888; margin-bottom: 16px; }
.form-card { margin-top: 12px; }
.amount-list { display: flex; flex-wrap: wrap; gap: 12px; }
.amount-tag { width: 100px; border: 2px solid #e8e8e8; border-radius: 8px; padding: 12px 0; text-align: center; cursor: pointer; transition: border-color .2s; }
.amount-tag.active { border-color: #00a854; background: #f0f9f5; }
.opt-label { font-size: 14px; font-weight: 600; }
.opt-pts { font-size: 12px; color: #f60; margin-top: 4px; }
</style>

