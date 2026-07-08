<template>
  <div>
    <h1 class="page-title">仪表盘</h1>
    <div class="stats-row" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总执行次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value green">{{ stats.success }}</div>
        <div class="stat-label">成功</div>
      </div>
      <div class="stat-card">
        <div class="stat-value red">{{ stats.failed }}</div>
        <div class="stat-label">失败</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.today_success }}/{{ stats.today_total }}</div>
        <div class="stat-label">今日成功/总数</div>
      </div>
    </div>
    <div class="quick-actions">
      <router-link to="/accounts" class="action-btn">管理签到账号</router-link>
      <router-link to="/records" class="action-btn action-secondary">查看签到记录</router-link>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() { return { stats: null } },
  async mounted() {
    try { this.stats = await api.getStats() } catch (_) {}
  }
}
</script>

<style scoped>
.page-title { font-size: 22px; margin-bottom: 24px; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-value.green { color: #27ae60; }
.stat-value.red { color: #e74c3c; }
.stat-label { font-size: 13px; color: #999; margin-top: 4px; }
.quick-actions { display: flex; gap: 12px; }
.action-btn { padding: 12px 24px; background: #4a6cf7; color: #fff; border-radius: 6px; text-decoration: none; font-size: 14px; }
.action-secondary { background: #fff; color: #4a6cf7; border: 1px solid #4a6cf7; }
</style>
