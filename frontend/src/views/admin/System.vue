<template>
  <div>
    <div class="page-title">系统设置</div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>基础配置</template>
          <el-form label-width="130px">
            <el-form-item label="商城名称">
              <el-input v-model="cfg.site_name" />
            </el-form-item>
            <el-form-item label="注册赠送积分">
              <el-input-number v-model="cfg.register_points" :min="0" />
            </el-form-item>
            <el-form-item label="积分兑换比例">
              <el-input-number v-model="cfg.points_rate" :min="1" />
              <span style="margin-left:8px;font-size:13px;color:#888">1元 = {{ cfg.points_rate }} 积分</span>
            </el-form-item>
            <el-form-item label="订单自动确收天数">
              <el-input-number v-model="cfg.auto_confirm_days" :min="1" :max="30" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>系统信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="数据库">MySQL 8.0</el-descriptions-item>
            <el-descriptions-item label="缓存">Redis 7.x</el-descriptions-item>
            <el-descriptions-item label="后端框架">FastAPI + SQLAlchemy 2.x</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const cfg = ref({ site_name: '中国移动积分商城', register_points: 200, points_rate: 100, auto_confirm_days: 7 })
function saveConfig() { ElMessage.success('配置已保存（演示模式）') }
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
</style>

