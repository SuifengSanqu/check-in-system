<template>
  <div>
    <div class="page-header">
      <button @click="$router.push('/accounts')" class="btn-back">返回账号列表</button>
      <h1 class="page-title" v-if="account">{{ account.name }}</h1>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="account" class="detail-card">
      <div class="info-grid">
        <div class="info-item"><span class="label">网站</span><span>{{ account.site_url }}</span></div>
        <div class="info-item"><span class="label">登录账号</span><span>{{ account.login_username }}</span></div>
        <div class="info-item"><span class="label">时间窗口</span><span>{{ account.time_window_start }} - {{ account.time_window_end }}</span></div>
        <div class="info-item"><span class="label">状态</span><span :class="account.enabled ? 'green' : 'red'">{{ account.enabled ? '已启用' : '已停用' }}</span></div>
      </div>
      <button @click="runCheckin" class="btn-run">立即执行签到</button>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() { return { account: null, loading: true } },
  async mounted() {
    const id = this.$route.params.id
    try { this.account = await api.getAccount(id) } finally { this.loading = false }
  },
  methods: {
    async runCheckin() {
      const result = await api.runAccount(this.account.id)
      if (result.status === 'success') {
        alert('签到成功')
      } else {
        alert('签到失败: ' + (result.error || result.message || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.page-title { font-size: 22px; }
.btn-back { padding: 6px 14px; background: #fff; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; font-size: 13px; }
.detail-card { background: #fff; padding: 28px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.label { font-size: 12px; color: #999; }
.green { color: #27ae60; }
.red { color: #e74c3c; }
.btn-run { padding: 10px 32px; background: #27ae60; color: #fff; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
.loading { text-align: center; padding: 60px; color: #999; }
</style>
